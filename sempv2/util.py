import requests
import json
import logging

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

def exec_rest_commands(rest_commands, retry_on="NOT_ALLOWED"):
    retry_commands = []
    for c in rest_commands:
        r = rest(c["verb"], BROKER_OPTIONS["config_url"]+c["url"], c["data_json"],
            return_error_status=True)
        if type(r) is requests.models.Response:
            if r.status_code == 400 and\
                safeget(r.json(), "meta", "error", "status") == retry_on:
                retry_commands.append(c)
                logging.warn("{:<6} {}, status:{}-{}".format(c["verb"].upper(), c["url"],\
                    r.status_code, retry_on))
            else:
                logging.error("{:<6} {}, status:{}".format(c["verb"].upper(), c["url"], r.status_code))
                if c["data_json"]: print(json.dumps(c["data_json"], indent=2))
                print(r.text)
                raise SystemExit
        else:
            logging.info("{:<6} {}, status:{}".format(c["verb"].upper(), c["url"], 200))

    if len(retry_commands) != len(rest_commands):
        exec_rest_commands(retry_commands)


def safeget(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct