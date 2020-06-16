import logging

from .util import *
from .backup import get_online_obj_config
from .sempv2_defs import *

def delete(top_coll_name, obj_name):
    if BROKER_OPTIONS["verbose"]:
        logging.info("About to delete : {}/{}/{}".format(\
            BROKER_OPTIONS["config_url"], top_coll_name, obj_name))
    
    obj_def = SEMPV2_DEFS[top_coll_name]
    vpn_config = get_online_obj_config(top_coll_name, obj_name)
    rest_commands = []
    generate_delete_commands(rest_commands, "", top_coll_name, vpn_config, obj_def)
    if BROKER_OPTIONS["curl_only"]:
        build_curl_commands(rest_commands)
    else:
        exec_rest_commands(rest_commands)

    
def generate_delete_commands(rest_commands, parent_uri, coll_name, obj_json, obj_def):
    #1. build the uri for current object
    id_uri = build_identifiers_uri(obj_json, obj_def)
    if is_build_in_object(obj_def, id_uri):
        # This is a built-in element, skip the delete operation
        return

    if id_uri.startswith("%23"):
        # Names starting with '#'->'%23' are reserved 
        # skip the delete operation
        return
    object_uri = parent_uri+"/"+coll_name+"/"+id_uri

    #2 Check if this object includes Requires-Disable attributes
    #if len(obj_def["RequiresDisable"]) > 0:
        # disable current element fist
        # payload = {"enabled":False}
        # append_rest_commands(rest_commands, "patch", object_uri, id_uri, payload)

    #3. recursively process all children
    for child_coll_name, child_obj_def in obj_def["Children"].items():
        if child_coll_name not in obj_json:
            continue
        for child_obj in obj_json[child_coll_name]:
            generate_delete_commands(rest_commands, object_uri, child_coll_name, child_obj, child_obj_def)

    #4. delete current element
    append_rest_commands(rest_commands, "delete", object_uri, id_uri)
