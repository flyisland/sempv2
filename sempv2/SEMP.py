import requests
import json

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

            if (len(list_of_data)>0):
                data[k_elements]=[]
                elements = data[k_elements]
    
            for i in range(len(list_of_data)):
                elements.append(list_of_data[i])
                self.__recursive_get_elements(elements[-1], list_of_links[i])
