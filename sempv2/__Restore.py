import json
from urllib.parse import quote_plus
import logging
from jinja2 import Template
import os
from jinja2 import Environment, FileSystemLoader

from  .util import append_rest_commands

class Mixin:
    def restore(self, filename):
        filedir=os.path.dirname(os.path.abspath(filename))
        filename=os.path.basename(filename)
        e = Environment(
            loader=FileSystemLoader(filedir), 
            trim_blocks=True, 
            lstrip_blocks=True)
        config_txt = e.get_template(filename).render()

        data = json.loads(config_txt)
        rest_commands = []
        self.__post_element(rest_commands, "", "msgVpns", data)
        for c in rest_commands:
            print("{} {} {}".format(c["verb"], c["url"], c["key_uri"]))
            print(json.dumps(c["data_json"]))

    def __post_element(self, rest_commands, url, elements_name, data):
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
            return

        #4.1 "Not allowed to modify sub-elements while the element is enabled."
        isEnable = False
        if self.IS_UNABLE_NEEDED_TO_MODIFY_SUBS in element_def:
            # disable current element fist
            if "enabled" in payload:
                isEnable = payload["enabled"]
            if isEnable:
                payload["enabled"]=False

        if key_uri in element_def.get("built_in_elements_quote_plus", []):
            # This is a existed built-in element
            # Patch to update existed element
            
            append_rest_commands(rest_commands, "patch", resource_url, key_uri, payload)
        else:
            # Post to create new element
            append_rest_commands(rest_commands, "post", collention_url, key_uri, payload)

        #5. recursively process all sub elements
        for sub_elements_name in element_def["sub_elements"]:
            if sub_elements_name not in data:
                continue
            for item in data[sub_elements_name]:
                self.__post_element(rest_commands, resource_url, sub_elements_name, item)

        #6. If needed, Enable this element again after all its sub-elements are settled
        if isEnable:
            payload = {"enabled":True}
            append_rest_commands(rest_commands, "patch", resource_url, key_uri, payload)
