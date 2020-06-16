import requests
from urllib.parse import quote_plus
import json
import re

from .util import rest

SEMPV2_BASE_PATH = "/SEMP/v2/config"
SEMP_VERSION_ONLINE = {}
SEMP_VERSION_FILE = {}
SEMPV2_DEFS = {}
__sempv2_openapi_config_json = None
__all_paths = None

def init_object_definitions(BROKER_OPTIONS):
    global SEMP_VERSION_ONLINE
    global SEMPV2_DEFS
    global __sempv2_openapi_config_json
    global __all_paths

# get sempVersion first
    api_url = BROKER_OPTIONS["config_url"]+"/about/api"
    api_json = rest("get", api_url)
    ver = api_json["data"]["sempVersion"]
    SEMP_VERSION_ONLINE["TEXT"]=ver
    # convert the string version into int so we could compare them
    SEMP_VERSION_ONLINE["INT"]=int(ver.split(".")[0])*1000+int(ver.split(".")[1])

# get the spec of semp
    spec_url = BROKER_OPTIONS["config_url"]+"/spec"
    __sempv2_openapi_config_json = rest("get", spec_url)
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

    # return None if there is no such resource there
    if (not __sempv2_openapi_config_json
        .get("paths")
        .get(collection_path)):
        return None

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


if __name__ == '__main__':
    init_object_definitions({
        "config_url":"http://localhost:8080/SEMP/v2/config", 
        "admin_user":"admin",
        "password":"admin"
    })
    print(json.dumps(SEMPV2_DEFS, indent=2))