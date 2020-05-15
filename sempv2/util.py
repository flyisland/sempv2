import requests
import json
from urllib.parse import quote_plus
import logging

# helper functions
BROKER_OPTIONS = {}
def rest(verb, url, data_json=None, return_error_status=False):
    global BROKER_OPTIONS
    headers={"content-type": "application/json"}
    r = getattr(requests, verb)(url, headers={"content-type": "application/json"},
        auth=(BROKER_OPTIONS["admin_user"], BROKER_OPTIONS["password"]),
        data=(json.dumps(data_json) if data_json != None else None))
    if (r.status_code != 200):
        if (return_error_status):
            return r
        else:
            print("{} on {} returns {}".format(verb.upper(), url, r.status_code))
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


def extract_payload(element_def, object_json):
    payload = {}
    for k in object_json:
        if k not in element_def["sub_elements"]:
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
