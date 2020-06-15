import requests
import json
from urllib.parse import quote_plus
import logging

from .sempv2_defs import SEMPV2_DEFS
# helper functions
BROKER_OPTIONS = {}
#    BROKER_OPTIONS["config_url"]
#    BROKER_OPTIONS["admin_user"]
#    BROKER_OPTIONS["password"]
#    BROKER_OPTIONS["verbose"]

def rest(verb, url, data_json=None, return_error_status=False):
    global BROKER_OPTIONS
    headers={"content-type": "application/json"}
    str_json = json.dumps(data_json,indent=2) if data_json != None else None
    r = getattr(requests, verb)(url, headers=headers,
        auth=(BROKER_OPTIONS["admin_user"], BROKER_OPTIONS["password"]),
        data=(str_json))
    if (r.status_code != 200):
        if (return_error_status):
            return r
        else:
            print("{} on {} returns {}".format(verb.upper(), url, r.status_code))
            if str_json: print(str_json)
            print(r.text)
            raise RuntimeError
    else:
        return r.json()

def build_identifiers_uri(obj_json, obj_def):
    """find out Identifiers and build the combined uri"""
    id_uri = ",".join([quote_plus(obj_json[id_name] if id_name in obj_json else "") for id_name in obj_def["Identifiers"]])
    return id_uri

def is_build_in_object(obj_def, id_uri):
    objs_has_build_in = ["aclProfileName", "clientProfileName", "clientUsername"]
    if id_uri == "default" and \
        obj_def["Identifiers"][0] in objs_has_build_in:
        return True
    else:
        return False


def extract_payload(obj_def, object_json):
    payload = {}
    for k in object_json:
        if k not in obj_def["Children"]:
            payload[k] = object_json[k]
    return payload


def append_rest_commands(commands, verb, url, key_uri="", data_json=None):
    commands.append({"verb":verb, 
        "url": url, 
        "key_uri":key_uri,
        "data_json":data_json
        })


def build_curl_commands(commands):
    print("#!/bin/sh +x")
    print("export HOST={}".format(BROKER_OPTIONS["config_url"]))
    print("export ADMIN={}".format(BROKER_OPTIONS["admin_user"]))
    print("export PWD={}".format(BROKER_OPTIONS["password"]))

    for c in commands:
        print("")
        curl_cmd = "curl -X {} -u $ADMIN:$PWD $HOST{}".format(c["verb"].upper(), c["url"])
        if (c["data_json"] !=None):
            curl_cmd += """ \\
-H 'content-type: application/json' -d '
{}'""".format(json.dumps(c["data_json"], indent=2))
        print(curl_cmd)

def exec_rest_commands(rest_commands):
    for c in rest_commands:
        logging.info("{:<6} {}".format(c["verb"].upper(), c["url"]))
        rest(c["verb"], BROKER_OPTIONS["config_url"]+c["url"], c["data_json"])


def remove_special_attributes(obj_def, data, parent_identifiers=[], remove_default_value=True, remove_reserved_object=True):
    """Remove attributes with default value"""
    
    #1. Remove attributes with default value
    if remove_default_value:
        Defaults = obj_def["Defaults"]
        for k, v in Defaults.items():
            if k in data and data[k] == Defaults[k]:
                data.pop(k)
    
    #2 remove identifiers of parent object, which are duplicated in each level
    for k in parent_identifiers:
        if k in data:
            data.pop(k)
    
    #3. recursively process all children
    parent_identifiers_for_child = parent_identifiers + obj_def["Identifiers"]
    for child_coll_name, child_obj_def in obj_def["Children"].items():
        if child_coll_name not in data: # skip empty elements
            continue
        
        # Names starting with '#'->'%23' are reserved
        # Remove it from backup
        if remove_reserved_object:
            data[child_coll_name][:] = [child_obj for child_obj in data[child_coll_name] \
                if not build_identifiers_uri(child_obj, child_obj_def).startswith("%23")]

        for child_obj in data[child_coll_name]:
            remove_special_attributes(child_obj_def, child_obj, parent_identifiers_for_child, remove_default_value, remove_reserved_object)


def remove_deprecated_children(obj_def, obj_json, deprecated_children=[]):
    for child_coll_name, child_obj_def in obj_def["Children"].items():
        if child_coll_name not in obj_json: # skip empty elements
            continue
        
        if child_obj_def.get("deprecated", False):
            deprecated_children.append(child_coll_name)
            obj_json.pop(child_coll_name)
            continue

        for child_obj in obj_json[child_coll_name]:
            remove_deprecated_children(child_obj_def, child_obj, deprecated_children)

def get_object_identifiers(top_coll_name):
    url = "{}/{}".format(BROKER_OPTIONS["config_url"], top_coll_name)
    
    # GET the first level content of this object
    rjson = rest("get", url)
    obj_list = rjson['data']
    obj_def = SEMPV2_DEFS[top_coll_name]
    return [build_identifiers_uri(obj_json, obj_def) for obj_json in obj_list ]
