import json

# helper functions

def append_rest_commands(commands, verb, url, key_uri="", data_json=None):
    commands.append({"verb":verb, 
        "url": url, 
        "key_uri":key_uri,
        "data_json":data_json
        })


def build_curl_commands(commands, config_url="", admin_user="", password=""):
    print("#!/bin/sh +x")
    print("export HOST={}".format(config_url))
    print("export ADMIN={}".format(admin_user))
    print("export PWD={}".format(password))

    for c in commands:
        print("")
        curl_cmd = "curl -X {} -u $ADMIN:$PWD $HOST{}".format(c["verb"].upper(), c["url"])
        if (c["data_json"] !=None):
            curl_cmd += """ \\
-H 'content-type: application/json' -d '
{}'""".format(json.dumps(c["data_json"], indent=2))
        print(curl_cmd)