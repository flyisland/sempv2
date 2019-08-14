import requests
import json
from importlib_resources import read_text
from urllib.parse import quote_plus

class SEMPv2:

    def __init__(self, host="", admin_user="", password=""):
        self.host = host
        self.admin_user = admin_user
        self.password = password
        self.config_url = "/SEMP/v2/config/msgVpns/"

    def backup_vpn(self, vpn_name):
        url = self.host+self.config_url+vpn_name
        # GET the first level content of this vpn
        rjson = self.__rest("get", url)
        self.vpn = rjson['data']
        links = rjson['links']

        # GET all its sub elements
        self.__recursive_get_elements(self.vpn, links)
        self.__remove_default_properties("msgVpns", self.vpn)
        print(json.dumps(self.vpn, indent=4))

    def __recursive_get_elements(self, data, links):
        for k_uri, v in links.items():
            if (k_uri == "uri"): # ignore link pointed to itself
                continue
            k_elements = k_uri[:-3]
            
            rjson = self.__rest("get", url)
            list_of_data = rjson['data']
            list_of_links = rjson['links']

            if (len(list_of_data)>0): # skip empty elements
                data[k_elements]=[]
                elements = data[k_elements]
    
            for i in range(len(list_of_data)):
                elements.append(list_of_data[i])
                self.__recursive_get_elements(elements[-1], list_of_links[i])

    def __remove_default_properties(self, element_name, data, unrequired_elements=[]):
        #1. read json file
        element_def = self.__load_def_json(element_name)
        
        #2. remove default properties
        for k, v in element_def["defaults"].items():
            if k in element_def["key_names"]:
                # must keep the required properties
                continue
            if k in data:
                if data[k] == element_def["defaults"][k]:
                    data.pop(k)
        
        #2.1 remove unrequired elements
        for k in unrequired_elements:
            if k in data:
                data.pop(k)
        sub_unrequired_elements = unrequired_elements + element_def["key_names"]

        #3. recursively process all sub elements
        for sub_name in element_def["sub_elements"]:
            if sub_name not in data: # skip empty elements
                continue
            for sub_element in data[sub_name]:
                self.__remove_default_properties(sub_name, sub_element, sub_unrequired_elements)

    def __load_def_json(self, element_name):
        # https://importlib-resources.readthedocs.io/en/latest/using.html
        # Reads contents with UTF-8 encoding and returns str.
        return json.loads(read_text('sempv2.sempv2_def', element_name+'.json'))
        
    
    def restore(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        url = self.host + "/SEMP/v2/config"
        self.__post_element(url, "msgVpns", data)


    def __post_element(self, url, elements_name, data):
        #1. load definition of this element
        element_def = self.__load_def_json(elements_name)

        #2. extract the payload of this element
        payload = {}
        for k in data:
            if k not in element_def["sub_elements"]:
                payload[k] = data[k]

        #3. post to create this resource
        elements_url = url+"/"+elements_name
        self.__rest("post", elements_url, payload)

        #4. build parent url for sub elements
        key_uri = ",".join([quote_plus(data[key_name]) for key_name in element_def["key_names"]])
        parent_url = elements_url+"/"+key_uri

        #5. recursively process all sub elements
        for sub_elements_name in element_def["sub_elements"]:
            if sub_elements_name not in data:
                continue
            for item in data[sub_elements_name]:
                self.__post_element(parent_url, sub_elements_name, item)

    def __rest(self, verb, url, data_json=None):
        auth=(self.admin_user, self.password)
        headers={"content-type": "application/json"}
        r = getattr(requests, verb)(url, headers={"content-type": "application/json"},
            auth=(self.admin_user, self.password),
            data=(json.dumps(data_json) if data_json != None else None))
        rjson = r.json()
        if (r.status_code != 200):
            print(r.text)
            raise RuntimeError
        else:
            return r.json()
