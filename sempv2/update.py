import logging
import re

from .sempv2_defs import SEMPV2_DEFS
from .backup import get_online_obj_config, remove_default_attributes
from .restore import read_config_file, generate_restore_commands
from .delete import generate_delete_commands
from .util import *

__update_password = False
def update(top_coll_name, filename, curl_command, update_password):
    global __update_password
    __update_password = update_password

    # 1. load config from file first
    obj_def = SEMPV2_DEFS[top_coll_name]
    obj_json_file = read_config_file(filename)
    remove_default_attributes(obj_def, obj_json_file)
    obj_name = build_identifiers_uri(obj_json_file, obj_def)    
    if BROKER_OPTIONS["verbose"]:
        logging.info("About to update the online object '{}/{}/{}' with file '{}'".format
            (BROKER_OPTIONS["config_url"], top_coll_name, obj_name, filename))

    # 2. load config from online vpn
    obj_json_online = get_online_obj_config(top_coll_name, obj_name)

    # 3. generate update rest commands
    rest_commands = []
    generate_update_commands(rest_commands, "", top_coll_name, obj_json_file,obj_json_online, obj_def)

    if(len(rest_commands) == 0):
        logging.info("The config file '{}' is identical to the online object '{}/{}/{}'.".format\
            (filename, BROKER_OPTIONS["config_url"], top_coll_name, obj_name))
        return

    if(curl_command):
        build_curl_commands(rest_commands)
    else:
        exec_rest_commands(rest_commands)

def generate_update_commands(rest_commands, parent_uri, coll_name, new_json, old_json, obj_def):

    #1. extract the payload of both new and old object
    new_payload = extract_payload(obj_def, new_json)
    old_payload = extract_payload(obj_def, old_json)

    #2. build collention url and object url for this object
    id_uri = build_identifiers_uri(old_json, obj_def)
    collention_uri = parent_uri+"/"+coll_name
    object_uri = collention_uri+"/"+id_uri

    #3. Names starting with '#'->'%23' are reserved 
    if id_uri.startswith("%23"):
        # just skip this reserved object
        return

    # 4. update_password check
    password_re = re.compile("password", re.IGNORECASE)
    if not __update_password:
        keys_include_pwd = [k for k in new_payload if re.search(password_re, k)]
        for k in keys_include_pwd:
            # remove all attributes include "password"
            new_payload.pop(k)
            logging.info("'{}' of {} will not be updated!".format(k, object_uri))

    # 5. Check if this config file includes Requires-Disable update
    is_disable_needed = False
    RequiresDisableAttrs = [k for k in obj_def["RequiresDisable"] if k in new_payload]
    if len(RequiresDisableAttrs) > 0:
        # disable current object fist
        if "enabled" in new_payload:
            is_disable_needed = new_payload["enabled"]

    if new_payload == old_payload:
        # same payload, no need to update other properties
        new_payload = {}

    if is_disable_needed:
        # disable this object to allow modifying its sub objects
        new_payload["enabled"]=False

    # 6. update current object
    if {"enabled":False} == new_payload:
        # just to disable current object
        append_rest_commands(rest_commands, "patch", object_uri, id_uri, new_payload)
    elif {} != new_payload:
        # new_payload != old_payload: use 'put' method to erase existed properties
        # with non-default values
        append_rest_commands(rest_commands, "put", object_uri, id_uri, new_payload)
    # else
        # {} == new_payload: nothing to do
    
    #7. recursively process all sub elements
    for child_coll_name, child_obj_def in obj_def["Children"].items():
        if child_coll_name in new_json:
            if child_coll_name in old_json:
                # This child_coll in both new and old json
                compare_two_collection(rest_commands, object_uri, child_coll_name, 
                    new_json[child_coll_name], old_json[child_coll_name], child_obj_def)
            else:
                # new only collection, create them
                for child_obj in new_json[child_coll_name]:
                    generate_restore_commands(rest_commands, object_uri, child_coll_name, child_obj, child_obj_def)
        elif child_coll_name in old_json:
            # old only collection, just delete them
            for child_obj in old_json[child_coll_name]:
                generate_delete_commands(rest_commands, object_uri, child_coll_name, child_obj, child_obj_def)
        else:
            continue

    #8. If needed, Enable this element again after all its sub-objects are settled
    if is_disable_needed:
        payload = {"enabled":True}
        append_rest_commands(rest_commands, "patch", object_uri, id_uri, payload)

    return

def compare_two_collection(rest_commands, object_url, coll_name, new_list, old_list, obj_def):
    while len(new_list)>0:
        find_match = False
        new_obj = new_list.pop(0)
        new_id_uri = build_identifiers_uri(new_obj, obj_def)
        for j, old_obj in enumerate(old_list):
            old_id_uri = build_identifiers_uri(old_obj, obj_def)
            if new_id_uri == old_id_uri:
                find_match = True
                break
        if find_match:
            generate_update_commands(rest_commands, object_url, coll_name, new_obj, old_obj, obj_def)
            old_list.pop(j)
        else:
            # this is a new only object
            generate_restore_commands(rest_commands, object_url, coll_name, new_obj, obj_def)

    # old only objects
    for old_obj in old_list:
        generate_delete_commands(rest_commands, object_url, coll_name, old_obj, obj_def)

    return