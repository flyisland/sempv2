import json
from .util import *
from .sempv2_defs import SEMPV2_DEFS

def backup(top_coll_name, obj_name, remove_default_value=False, reserve_deprecated=False):
    vpn_config = get_online_obj_config(top_coll_name, obj_name, remove_default_value, reserve_deprecated)
    print(json.dumps(vpn_config, indent=2))

def get_online_obj_config(top_coll_name, obj_name, remove_default_value=False, reserve_deprecated=False):
    url = "{}/{}/{}".format(BROKER_OPTIONS["config_url"], top_coll_name, obj_name)
    
    # GET the first level content of this object
    rjson = rest("get", url)
    obj_config = rjson['data']
    links = rjson['links']

    # GET all children collections
    fetch_collections(obj_config, links)
    obj_def = SEMPV2_DEFS[top_coll_name]
    if remove_default_value:
        remove_default_attributes(obj_def, obj_config)
    if not reserve_deprecated:
        remove_deprecated_children(obj_def, obj_config)
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

