import requests
import json
from importlib_resources import read_text
from urllib.parse import quote_plus
import logging

from  sempv2 import __Backup, __Delete, __Restore, __Update

logging.basicConfig(level=logging.INFO)

class SEMPv2(__Backup.Mixin, __Delete.Mixin, __Restore.Mixin, __Update.Mixin):
    IS_UNABLE_NEEDED_TO_MODIFY_SUBS = "isUnableNeedToModifySubs"

    def __init__(self, host="", admin_user="", password=""):
        self.admin_user = admin_user
        self.password = password
        self.config_url = host + "/SEMP/v2/config"

    def load_def_json(self, element_name):
        # https://importlib-resources.readthedocs.io/en/latest/using.html
        # Reads contents with UTF-8 encoding and returns str.
        return json.loads(read_text('sempv2.sempv2_def', element_name+'.json'))
        
    
    def rest(self, verb, url, data_json=None, return_error_status=False):
        auth=(self.admin_user, self.password)
        headers={"content-type": "application/json"}
        r = getattr(requests, verb)(url, headers={"content-type": "application/json"},
            auth=(self.admin_user, self.password),
            data=(json.dumps(data_json) if data_json != None else None))
        if (r.status_code != 200):
            if (return_error_status):
                return r
            else:
                print(r.text)
                raise RuntimeError
        else:
            return r.json()

    def build_key_uri(self, element_json, element_def):
        key_uri = ",".join([quote_plus(element_json[key_name] if key_name in element_json else "") for key_name in element_def["key_names"]])
        return key_uri
