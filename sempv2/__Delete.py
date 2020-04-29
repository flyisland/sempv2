import logging

from .util import append_rest_commands, build_curl_commands

class Mixin:

    def delete_vpn(self, vpn_name):
        self.get_vpn_config(vpn_name)
        rest_commands = []
        self.generate_delete_commands(rest_commands, "", "msgVpns", self.vpn)
        if(self.curl_command):
            build_curl_commands(rest_commands, self.config_url, self.admin_user, self.password)
        else:
            self.exec_rest_commands(rest_commands)

        
    def generate_delete_commands(self, rest_commands, url, elements_name, data):
        #1. read json file
        element_def = self.load_def_json(elements_name)

        #2. build resource url for current element
        key_uri = self.build_key_uri(data, element_def)
        if key_uri in element_def.get("built_in_elements_quote_plus", []):
            # This is a built-in element, skip the delete operation
            return

        if key_uri.startswith("%23"):
            # Names starting with '#'->'%23' are reserved 
            # skip the delete operation
           return
        object_url = url+"/"+elements_name+"/"+key_uri

        #2.1 "Not allowed to modify sub-elements while the element is enabled."
        if self.IS_UNABLE_NEEDED_TO_MODIFY_SUBS in element_def:
            # disable current element fist
            payload = {"enabled":False}
            append_rest_commands(rest_commands, "patch", object_url, key_uri, payload)

        #3. recursively process all sub elements
        for sub_name in reversed(element_def["sub_elements"]):
            if sub_name not in data: # skip empty elements
                continue
            for sub_element in data[sub_name]:
                self.generate_delete_commands(rest_commands, object_url, sub_name, sub_element)

        #4. delete current element
        append_rest_commands(rest_commands, "delete", object_url, key_uri)
