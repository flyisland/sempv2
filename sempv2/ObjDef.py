import json
import re

# [Download SEMP Specification JSON](https://products.solace.com/download/PUBSUB_SEMPV2_SCHEMA_JSON)
# version  2.15
SEMPV2_API_VERSION="2.15"
sempv2_openapi_config_json = json.loads(\
    open("./semp-v2-swagger-config.json", "r").read())
BASE_PATH = sempv2_openapi_config_json['basePath']
MSGVPN_DEF = {}

def initObjectDefinitions():
    global MSGVPN_DEF
    MSGVPN_DEF = buildObjDef("", "msgVpns")
   


__all_paths =  sempv2_openapi_config_json['paths'].keys()
def buildObjDef(parent_path, collection_name):
    this_def = {}
    # 1. find the collection path and the object path
    collection_path = parent_path + "/" + collection_name
    if(sempv2_openapi_config_json
        .get("paths")
        .get(collection_path)
        .get("get")
        .get("deprecated")):
        # This has been deprecated, just skip it.
        return None

    obj_re = re.compile("^"+collection_path+"/{[^/]+}$")
    obj_path = [path for path in __all_paths if re.search(obj_re, path)][0]

    # 2. find out attributes like "Identifiers", "WriteOnly", "RequiresDisable", 
    # and skip "Deprecated"
    # 3. find out attributes with default value
    id_re = re.compile("{([^}]+)}")
    Identifiers = re.findall(id_re, obj_path.split("/")[-1])
    this_def['Identifiers'] = Identifiers

    obj_path_json = sempv2_openapi_config_json["paths"][obj_path]
    this_def = {**this_def, \
        ** findSpecialAttributes(obj_path_json), \
        ** findDefaultValues(obj_path_json)}

    # 4. find out all children collection name from paths
    childrenRe = re.compile(obj_path+"/([^/]+)$")
    childrenCollectionNames = [re.search(childrenRe, path).group(1) for path in __all_paths if re.search(childrenRe, path)]

    this_def["Children"] = {}
    for coll_name in childrenCollectionNames:
        childDef = buildObjDef(obj_path, coll_name)
        # skip deprecated one
        if not childDef : continue           
        this_def["Children"][coll_name] = buildObjDef(obj_path, coll_name)

    return this_def


def findSpecialAttributes(obj_path_json):
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


def findDefaultValues(obj_path_json):
    patch = obj_path_json.get("patch")
    if not patch:
        return {"Defaults": {}}

    ref = [p["schema"]["$ref"] for p in patch["parameters"] if p.get("name")=="body"][0]
    definition = ref.split("/")[-1]

    return {"Defaults": findDefaultValuesFromDefinitions(definition)}

# Example: The default value is `false`.
__valueRe = re.compile("The default value is `([^`]+)`\.")
def findDefaultValuesFromDefinitions(definition):
    properties = sempv2_openapi_config_json["definitions"][definition]["properties"]

    Defaults = {}
    for key in properties:
        p = properties[key]
        description = p.get("description", "")
        match = re.search(__valueRe, description)
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
    initObjectDefinitions()
    print(json.dumps(MSGVPN_DEF, indent=2))
