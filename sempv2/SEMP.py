import requests
import json
from importlib_resources import read_text

class SEMPv2:

    def __init__(self, host="", admin_user="", password=""):
        self.host = host
        self.admin_user = admin_user
        self.password = password
        self.config_url = "/SEMP/v2/config/msgVpns/"

    def backup_vpn(self, vpn_name):
        url = self.host+self.config_url+vpn_name
        r = requests.get(url, auth=(self.admin_user, self.password))
        rjson = r.json()
        if (r.status_code != 200):
            print(json.dumps(rjson['meta'], indent=4))
        else:
            self.vpn = rjson['data']
            links = rjson['links']
            self.__recursive_get_elements(self.vpn, links)
            self.__remove_default_properties("msgVpns", self.vpn)
            print(json.dumps(self.vpn, indent=4))

    def __recursive_get_elements(self, data, links):
        for k_uri, v in links.items():
            if (k_uri == "uri"): # ignore link pointed to itself
                continue
            k_elements = k_uri[:-3]
            r = requests.get(v, auth=(self.admin_user, self.password))
            rjson = r.json()
            if (r.status_code != 200):
                print(json.dumps(rjson['meta'], indent=4))
                # TODO retrun error

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
        
