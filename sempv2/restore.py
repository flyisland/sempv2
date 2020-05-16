import json
from urllib.parse import quote_plus
import logging
from jinja2 import Template
import os
from jinja2 import Environment, FileSystemLoader

from .util import *
from .sempv2_defs import SEMPV2_DEFS

def restore(top_coll_name, filename, curl_command):
    if BROKER_OPTIONS["verbose"]:
        logging.info("About to restore {} with file '{}'".format(top_coll_name, filename))

    obj_json = read_config_file(filename)
    obj_def = SEMPV2_DEFS[top_coll_name]
    rest_commands = []
    generate_restore_commands(rest_commands, "", top_coll_name, obj_json, obj_def)
    if(curl_command):
        build_curl_commands(rest_commands)
    else:
        exec_rest_commands(rest_commands)

def read_config_file(filename):
    """Read the config json file and perform jinja2 templating"""
    
    filedir=os.path.dirname(os.path.abspath(filename))
    filename=os.path.basename(filename)
    e = Environment(
        loader=FileSystemLoader(filedir), 
        trim_blocks=True, 
        lstrip_blocks=True)
    config_txt = e.get_template(filename).render()
    return json.loads(config_txt)

def generate_restore_commands(rest_commands, parent_uri, coll_name, obj_json, obj_def):
    """ Generate rest commands to restore resources from `obj_json` """

    #1. extract the payload of this object
    payload = extract_payload(obj_def, obj_json)

    #2. build collention url and object url for this object
    id_uri = build_identifiers_uri(obj_json, obj_def)
    collention_uri = parent_uri+"/"+coll_name
    object_uri = collention_uri+"/"+id_uri

    # 3. check if this is a reserved object
    if id_uri.startswith("%23"):
        # Names starting with '#'->'%23' are reserved 
        # skip the restore operation
        return

    # 4. Check if this object includes Requires-Disable update
    isEnable = False
    RequiresDisableAttrs = [k for k in obj_def["RequiresDisable"] if k in payload]
    if len(RequiresDisableAttrs) > 0:
        # disable current object fist
        if "enabled" in payload:
            isEnable = payload["enabled"]
        if isEnable:
            payload["enabled"]=False

    if is_build_in_object(obj_def, id_uri):
        # This is a existed built-in object
        # Patch to update this existed object
        append_rest_commands(rest_commands, "patch", object_uri, id_uri, payload)
    else:
        # Post to create new object
        append_rest_commands(rest_commands, "post", collention_uri, id_uri, payload)

    #5. recursively process all children
    for child_coll_name, child_obj_def in obj_def["Children"].items():
        if child_coll_name not in obj_json:
            continue
        for child_obj in obj_json[child_coll_name]:
            generate_restore_commands(rest_commands, object_uri, child_coll_name, child_obj, child_obj_def)

    #6. If needed, Enable this object again after all its sub-elements are settled
    if isEnable:
        payload = {"enabled":True}
        append_rest_commands(rest_commands, "patch", object_uri, id_uri, payload)
