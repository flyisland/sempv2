import json
from urllib.parse import quote_plus
import logging


class Mixin:
    def restore(self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        self.__post_element(self.config_url, "msgVpns", data)


    def __post_element(self, url, elements_name, data):
        #1. load definition of this element
        element_def = self.load_def_json(elements_name)

        #2. extract the payload of this element
        payload = {}
        for k in data:
            if k not in element_def["sub_elements"]:
                payload[k] = data[k]

        #3. build collention url and resource url for this element
        key_uri = self.build_key_uri(data, element_def)
        collention_url = url+"/"+elements_name
        resource_url = collention_url+"/"+key_uri

        #4. post or patch to create this resource
        if key_uri.startswith("%23"):
            # Names starting with '#'->'%23' are reserved 
            # skip the restore operation
            logging.info("%s: %s" % ("skip", resource_url))
            return

        if key_uri in element_def.get("built_in_elements_quote_plus", []):
            # This is a existed built-in element
            # Patch to update existed element
            logging.info("%s: %s" % ("patch", resource_url))
            self.rest("patch", resource_url, payload)
        else:
            # Post to create new element
            logging.info("%s: %s with (%s)" % ("create", collention_url, key_uri))
            self.rest("post", collention_url, payload)

        #5. recursively process all sub elements
        for sub_elements_name in element_def["sub_elements"]:
            if sub_elements_name not in data:
                continue
            for item in data[sub_elements_name]:
                self.__post_element(resource_url, sub_elements_name, item)
