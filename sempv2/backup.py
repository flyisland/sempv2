import json
from .util import *
from .sempv2_defs import SEMPV2_DEFS

def backup_vpn(vpn_name):
    vpn_config = get_obj_config("msgVpns", vpn_name)
    print(json.dumps(vpn_config, indent=2))

def get_obj_config(top_coll_name, obj_name):
    url = "{}/{}/{}".format(BROKER_OPTIONS["config_url"], top_coll_name, obj_name)
    
    # GET the first level content of this object
    rjson = rest("get", url)
    obj_config = rjson['data']
    links = rjson['links']

    # GET all children collections
    fetch_collections(obj_config, links)
    obj_def = SEMPV2_DEFS[top_coll_name]
    remove_default_attributes(obj_def, obj_config)
    return obj_config

def fetch_collections(data, links):
    """Fetch all collection from `links`, then add them into `data` """
    for k_uri, url in links.items():
        if (k_uri == "uri"): # ignore the link pointed to itself
            continue
        k_elements = url.split("/")[-1]
        
        list_of_data = []
        list_of_links = []
        hasNextPage = True

        while hasNextPage:
            rjson = rest("get", url)
            list_of_data.extend(rjson['data'])
            list_of_links.extend(rjson['links'])

            if "meta" not in rjson:
                hasNextPage = False
            elif "paging" not in rjson["meta"]:
                hasNextPage = False
            elif "nextPageUri" not in rjson["meta"]["paging"]:
                hasNextPage = False
            else:
                url=rjson["meta"]["paging"]["nextPageUri"]

        if (len(list_of_data)>0): # skip empty objects
            data[k_elements]=[]
            elements = data[k_elements]

        for i in range(len(list_of_data)):
            elements.append(list_of_data[i])
            fetch_collections(elements[-1], list_of_links[i])

def remove_default_attributes(obj_def, data, parent_identifiers=[]):
    """Remove attributes with default value"""
    
    #1. Remove attributes with default value
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
        data[child_coll_name][:] = [child_obj for child_obj in data[child_coll_name] \
            if not build_identifiers_uri(child_obj, child_obj_def).startswith("%23")]

        for child_obj in data[child_coll_name]:
            remove_default_attributes(child_obj_def, child_obj, parent_identifiers_for_child)
