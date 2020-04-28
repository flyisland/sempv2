

class Mixin:
    def update(self, filename):
        # 1. load the config from file first
        config = self.read_config_file(filename)
        msgVpnName = config["msgVpnName"]

        # 2. then get the config from VPN
        self.get_vpn_config(msgVpnName)

        # 3. compare `self.vpn` with config
        
        return