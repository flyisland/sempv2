from urllib.parse import quote_plus
import logging

class Mixin:

    def delete_vpn(self, vpn_name):
            self.get_vpn_config(vpn_name)
            self.__delete_elements(self.config_url, "msgVpns", self.vpn)
        
    def __delete_elements(self, url, elements_name, data):
        #1. read json file
        element_def = self.load_def_json(elements_name)

        #2. build resource url for current element
        key_uri = ",".join([quote_plus(data[key_name]) for key_name in element_def["key_names"]])
        if key_uri in element_def.get("built_in_elements_quote_plus", []):
            # This is a built-in element, skip the delete operation
            return

        if key_uri.startswith("%23"):
            # Names starting with '#'->'%23' are reserved 
            # skip the delete operation
           return
        current_url = url+"/"+elements_name+"/"+key_uri

        #3. recursively process all sub elements
        for sub_name in element_def["sub_elements"]:
            if sub_name not in data: # skip empty elements
                continue
            for sub_element in data[sub_name]:
                self.__delete_elements(current_url, sub_name, sub_element)

        #4. delete current element
        logging.info("delete: %s" % (current_url))
        self.rest("delete", current_url)