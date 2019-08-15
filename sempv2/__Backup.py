import json

class Mixin:

    def backup_vpn(self, vpn_name):
        self.get_vpn_config(vpn_name)
        print(json.dumps(self.vpn, indent=4))

    def recursive_get_elements(self, data, links):
        for k_uri, url in links.items():
            if (k_uri == "uri"): # ignore link pointed to itself
                continue
            k_elements = k_uri[:-3]
            
            rjson = self.rest("get", url)
            list_of_data = rjson['data']
            list_of_links = rjson['links']

            if (len(list_of_data)>0): # skip empty elements
                data[k_elements]=[]
                elements = data[k_elements]
    
            for i in range(len(list_of_data)):
                elements.append(list_of_data[i])
                self.recursive_get_elements(elements[-1], list_of_links[i])

    def remove_default_properties(self, element_name, data, unrequired_elements=[]):
        #1. read json file
        element_def = self.load_def_json(element_name)
        
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
                self.remove_default_properties(sub_name, sub_element, sub_unrequired_elements)