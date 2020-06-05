import requests
import json
from importlib_resources import read_text
import re

SEMPV2_BASE_PATH = "/SEMP/v2/config"
SEMPV2_DEFS = {}
__sempv2_openapi_config_json = None
__all_paths = None

def init_object_definitions(BROKER_OPTIONS):
    global SEMPV2_DEFS
    global __sempv2_openapi_config_json
    global __all_paths

    spec_url = BROKER_OPTIONS["config_url"]+"/spec"
    r = requests.get(spec_url, \
        auth=(BROKER_OPTIONS["admin_user"], BROKER_OPTIONS["password"]))
    if (r.status_code != 200):
        print("GET on {} returns {}".format(spec_url, r.status_code))
        print(r.text)
        raise RuntimeError
    else:
        __sempv2_openapi_config_json = r.json()
        __all_paths =  __sempv2_openapi_config_json['paths'].keys()

    for coll in ["msgVpns", "dmrClusters"]:
        SEMPV2_DEFS[coll] = build_obj_def("", coll)
   


def build_obj_def(parent_path, collection_name):
    global SEMPV2_DEFS
    global __sempv2_openapi_config_json
    global __all_paths

    this_def = {}
    # 1. find the collection path and the object path
    collection_path = parent_path + "/" + collection_name
    if(__sempv2_openapi_config_json
        .get("paths")
        .get(collection_path)
        .get("get")
        .get("deprecated")):
        # This has been deprecated!
        this_def["deprecated"]=True

    obj_re = re.compile("^"+collection_path+"/{[^/]+}$")
    obj_path = [path for path in __all_paths if re.search(obj_re, path)][0]

    # 2. find out attributes like "Identifiers", "WriteOnly", "RequiresDisable", 
    # 3. find out attributes with default value
    # /msgVpns/{msgVpnName}/aclProfiles/{aclProfileName}/publishTopicExceptions/{publishTopicExceptionSyntax},{publishTopicException}
    id_re = re.compile("{([^}]+)}")
    Identifiers = re.findall(id_re, obj_path.split("/")[-1])
    this_def['Identifiers'] = Identifiers

    obj_path_json = __sempv2_openapi_config_json["paths"][obj_path]
    this_def = {**this_def, \
        ** __find_special_attributes(obj_path_json), \
        ** find_default_values(obj_path_json)}

    # 4. find out all children collection name from paths
    children_re = re.compile(obj_path+"/([^/]+)$")
    children_coll_names = [re.search(children_re, path).group(1) for path in __all_paths if re.search(children_re, path)]

    this_def["Children"] = {}
    for coll_name in children_coll_names:
        child_ef = build_obj_def(obj_path, coll_name)
        this_def["Children"][coll_name] = child_ef

    return this_def


def __find_special_attributes(obj_path_json):
    description = obj_path_json["patch"]["description"] if \
        obj_path_json.get("patch") else ""

    WriteOnly = []
    RequiresDisable = []
    xre = re.compile("^([^|]+)\|[^|]*\|[^|]*\|([^|]*)\|([^|]*)\|[^|]*$")

    for line in description.splitlines():
        m = re.search(xre, line)
        if m :
            if m.group(2) == "x":
                WriteOnly.append(m.group(1))
            if m.group(3) == "x":
                RequiresDisable.append(m.group(1))
    
    return {"WriteOnly": WriteOnly, "RequiresDisable": RequiresDisable}


def find_default_values(obj_path_json):
    patch = obj_path_json.get("patch")
    if not patch:
        return {"Defaults": {}}

    ref = [p["schema"]["$ref"] for p in patch["parameters"] if p.get("name")=="body"][0]
    definition = ref.split("/")[-1]

    return {"Defaults": __findDefaultValuesFromDefinitions(definition)}

# Example: The default value is `false`.
__value_re = re.compile("The default value is `([^`]+)`\.")
def __findDefaultValuesFromDefinitions(definition):
    properties = __sempv2_openapi_config_json["definitions"][definition]["properties"]

    Defaults = {}
    for key in properties:
        p = properties[key]
        description = p.get("description", "")
        match = re.search(__value_re, description)
        if not match: continue
        pType = p["type"]
        if   "integer" == pType:
            Defaults[key] = int(match.group(1))
        elif "boolean" == pType:
            Defaults[key] = True if match.group(1) == "true" else False
        elif "string"  == pType:
            # remove quote marks at both the begin and the end
            Defaults[key] = match.group(1)[1:-1]
        else:
            print("{} = {}".format(pType, match.group(1)))

    return Defaults

if __name__ == '__main__':
    init_object_definitions({
        "config_url":"http://localhost:8080/SEMP/v2/config", 
        "admin_user":"admin",
        "password":"admin"
    })
    print(json.dumps(SEMPV2_DEFS, indent=2))