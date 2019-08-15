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

        #3. post to create this resource
        elements_url = url+"/"+elements_name
        self.rest("post", elements_url, payload)

        #4. build parent url for sub elements
        key_uri = ",".join([quote_plus(data[key_name]) for key_name in element_def["key_names"]])
        parent_url = elements_url+"/"+key_uri
        logging.info("%s: %s" % ("create", parent_url))

        #5. recursively process all sub elements
        for sub_elements_name in element_def["sub_elements"]:
            if sub_elements_name not in data:
                continue
            for item in data[sub_elements_name]:
                self.__post_element(parent_url, sub_elements_name, item)
