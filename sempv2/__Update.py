from  .util import *

class Mixin:
    def update(self, filename):
        # 1. load config from file first
        data = self.read_config_file(filename)
        self.remove_default_properties("msgVpns", data)

        # 2. load config from online vpn
        msgVpnName = data["msgVpnName"]
        self.get_vpn_config(msgVpnName)

        # 3. generate update rest commands
        rest_commands = []
        self.generate_update_commands(rest_commands, "", "msgVpns", data, self.vpn)
        if(self.curl_command):
            build_curl_commands(rest_commands, self.config_url, self.admin_user, self.password)
        else:
            self.exec_rest_commands(rest_commands)
        return

    def generate_update_commands(self, rest_commands, url, elements_name, new_json, old_json):

        #1. load definition of this element
        element_def = self.load_def_json(elements_name)

        #2. extract the payload of both new and old object
        new_payload = extract_payload(element_def, new_json)
        old_payload = extract_payload(element_def, old_json)

        #3. build collention url and resource url for this element
        key_uri = self.build_key_uri(new_json, element_def)
        collention_url = url+"/"+elements_name
        object_url = collention_url+"/"+key_uri

        #4. Names starting with '#'->'%23' are reserved 
        if key_uri.startswith("%23"):
            # just skip this reserved object
            return

        #5. Do we need to care about this "enabled" property?
        is_unable_needed = False
        if self.IS_UNABLE_NEEDED_TO_MODIFY_SUBS in element_def:
            # disable current element fist
            if "enabled" in new_payload:
                is_unable_needed = new_payload["enabled"]

        if new_payload == old_payload:
            # same payload, no need to update other properties
            new_payload = {}

        if is_unable_needed:
            # disable this object to allow modifying its sub objects
            new_payload["enabled"]=False

        #6. update current object
        if {"enabled":False} == new_payload:
            # just disable current object
            append_rest_commands(rest_commands, "patch", object_url, key_uri, new_payload)
        elif {} != new_payload:
            # new_payload != old_payload: use 'put' method to erase existed properties
            # with non-default values
            append_rest_commands(rest_commands, "put", object_url, key_uri, new_payload)
        # else
            # {} == new_payload: nothing to do
        
        current_list_len = len(rest_commands)
        #7. recursively process all sub elements
        for sub_elements_name in element_def["sub_elements"]:
            if sub_elements_name in new_json:
                if sub_elements_name in old_json:
                    # check each objects in both sub_elements list
                    self.handle_obj_lists(rest_commands, object_url, sub_elements_name, 
                        new_json[sub_elements_name], old_json[sub_elements_name])
                else:
                    # new only sub_elements
                    for sub_obj in new_json[sub_elements_name]:
                        self.generate_restore_commands(rest_commands, object_url, sub_elements_name, sub_obj)
            elif sub_elements_name in old_json:
                # old only sub_elements
                for sub_obj in new_json[sub_elements_name]:
                    self.generate_delete_commands(rest_commands, object_url, sub_elements_name, sub_obj)
            else:
                continue

        #8. If needed, Enable this element again after all its sub-objects are settled
        if is_unable_needed:
            if len(rest_commands) == current_list_len:
                # no sub-objects needs to process, so no need to set enabled=False
                if {"enabled":False} == rest_commands[-1].data_json:
                    # new_payload == old_payload: nothing to do
                    rest_commands.pop(-1)
                else:
                    rest_commands[-1].data_json["enabled":True]
            else:
                payload = {"enabled":True}
                append_rest_commands(rest_commands, "patch", object_url, key_uri, payload)

        return

    def handle_obj_lists(self, rest_commands, object_url, elements_name, new_list, old_list):
        element_def = self.load_def_json(elements_name)
        #3. build collention url and resource url for this element
        while len(new_list)>0:
            find_match = False
            new_obj = new_list.pop(0)
            new_key_uri = self.build_key_uri(new_obj, element_def)
            for j, old_obj in enumerate(old_list):
                old_key_uri = self.build_key_uri(old_obj, element_def)
                if new_key_uri == old_key_uri:
                    find_match = True
                    break
            if find_match:
                self.generate_update_commands(rest_commands, object_url, elements_name, new_obj, old_obj)
                old_list.pop(j)
            else:
                # this is a new only object
                self.generate_restore_commands(rest_commands, object_url, elements_name, new_obj)

        # old only objects
        for old_obj in old_list:
            self.generate_delete_commands(rest_commands, object_url, elements_name, old_obj)

        return