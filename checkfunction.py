import os
import requests
from netaddr import *
from getmac import get_mac_address
class ConfigModem():
    def get_gateway_mac(self, ip='192.168.1.1'):
        try:
            mac_lan = get_mac_address(ip=ip).replace(':', '').upper()
            # mac_lan = get_mac_address(ip = ip)
        except:
            mac_lan = ''
        mac_wan = ''
        try:
            mac_lan_int = EUI(mac_lan).value
            # mac_lan_str = str(EUI(mac_lan_int + 6))
            mac_wan = str(EUI(mac_lan_int + 6)).replace("-", "")
        except:
            pass
        # Địa chỉ mac của mạng lan và địa chỉ mac của mạng wan
        return mac_lan, mac_wan
    

class AC1000V3:
    def __init__(self, username, password, wan_account='', wan_password='',
                 wifi_24_ssid='', wifi_24_pass='', wifi_24_mode='', wifi_24_channel='', wifi_24_bandwidth='',
                 wifi_5_ssid='', wifi_5_pass='', wifi_5_mode='', wifi_5_channel='', wifi_5_bandwidth=''):
        self.session = requests.Session()
        self.username = username
        self.password = password

        self.wan_account = wan_account
        self.wan_password = wan_password

        self.wifi_24_ssid = wifi_24_ssid
        self.wifi_24_pass = wifi_24_pass
        self.wifi_24_mode = wifi_24_mode
        self.wifi_24_channel = wifi_24_channel
        self.wifi_24_bandwidth = wifi_24_bandwidth

        self.wifi_5_ssid = wifi_5_ssid
        self.wifi_5_pass = wifi_5_pass
        self.wifi_5_mode = wifi_5_mode
        self.wifi_5_channel = wifi_5_channel
        self.wifi_5_bandwidth = wifi_5_bandwidth

    
    def get_password(self, mac_wan):
        p = os.popen("pass.exe " + mac_wan).read()
        pass_ = str(p.replace("passwd:", "").replace(
            " ", "").replace("\n", ""))
        return pass_

    def get_device_info(self):
        
        url = 'http://192.168.1.1/devinfo.html'
        r = self.session.get(url)
        info = r.content.decode('utf-8').split('\n')
        dev_name = ''
        firmware = ''
        power = ''
        dev_id = ''
        # print(info)
        for line in info:
            if 'dev_name =' in line and 'var' not in line:
                dev_name += line
            if 'dev_id =' in line and 'var' not in line:
                dev_id += line
            if 'sw_ver = ' in line and 'var' not in line:
                firmware += line
            if 'rxpower=' in line and 'var' not in line:
                power += line
        dev_name = dev_name.replace(';', '').replace(
            'dev_name = ', '').replace('"', '').strip()
        firmware = firmware.replace(';', '').replace(
            'sw_ver = ', '').replace('"', '').strip()
        # dev_id = dev_id.replace(';', '').replace(
        #     'dev_id = ', '').replace('"', '').strip()
        power = power.replace('rxpower=', '').replace(';', '').replace('"', '')
        try:
            power = str(round(float(power) / 500 - 30, 2))
        except:
            power = '---'
            
    
        return dev_name, power, firmware
    def login(self):
        url = 'http://192.168.1.1/GponForm/LoginForm'
        values = {
            "XRanID": self.username + self.password + "devinfo",
            "XWebPageName": "devinfo",
            "XNonce": "",
            "username": self.username,
            "password": self.password
        }
        r = self.session.post(url, data=values)
        return r.status_code
    
    
    def config_24G(self):
        url = 'http://192.168.1.1/GponForm/wifibasic_XForm'
        values = {
            "XWebPageName": "wifibasic",
            "wireless_radio": "1",
            "wifi_mode": self.wifi_24_mode,
            "channel_bandwidth": self.wifi_24_bandwidth,
            "channel": self.wifi_24_channel,
            "power_level": "0",
            "max_clients": "5",
            "wifi_multicast": "1"
        }
        r = self.session.post(url, data=values)
        
        return r.status_code

    def config_5G(self):
        pass
    def config_wan(self):
        pass
    def update_firmware(self):
        pass
    def check_login_status(self):
        response = self.session.get("http://192.168.1.1/index.html")
        # print(response.status_code)
        
        
        if response.status_code == 200:
            return True  # Đăng nhập còn duy trì
        elif response.status_code in (401, 403):
            return False  # Phiên đăng nhập đã hết hạn hoặc đã bị đăng xuất
        else:
            return None  # Không thể xác định trạng thái đăng nhập

if __name__ == "__main__":
    modem = ConfigModem()
    # model = G97RG_Model()
    mac_lan, mac_wan = modem.get_gateway_mac("192.168.1.1")
    print(mac_lan, mac_wan)
    ac1000v3 = AC1000V3('admin', '1965815728')
    password = ac1000v3.get_password(mac_wan)
    print(password)
    login_code = ac1000v3.login()
    print(login_code)
    if login_code == 200:
        dev_name, power, firmware = ac1000v3.get_device_info()
        print(dev_name, power, firmware)
        print(ac1000v3.check_login_status())
    
    # dev_name, firmware, power = ac1000v3.get_device_info()
    # print(dev_name, firmware, power)
    
    # if login_code == 200:
    #     status = ac1000v3.config_24G()
    #     print(status)
        # print(check)
