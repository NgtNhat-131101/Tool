import os
import requests
from netaddr import *
from getmac import get_mac_address
from bs4 import BeautifulSoup

class ConfigModem():
    def get_gateway_mac(self, ip='192.168.1.1'):
        try:
            mac_lan = get_mac_address(ip=ip).replace(':', '').upper()
        except:
            mac_lan = ''
        mac_wan = ''
        try:
            mac_lan_int = EUI(mac_lan).value
            mac_wan = str(EUI(mac_lan_int + 6)).replace("-", "")
        except:
            pass
        return mac_lan, mac_wan

class G97RG_Model():
    def __init__(self, dev_username, dev_password, wan_account='', wan_password='',
            wifi_24_ssid='', wifi_24_pass='', wifi_24_mode='', wifi_24_channel='', wifi_24_bandwidth='',
            wifi_5_ssid='' , wifi_5_pass='' , wifi_5_mode='' , wifi_5_channel='' , wifi_5_bandwidth=''):
        self.session = requests.Session()
        self.dev_username = dev_username
        self.dev_password = dev_password
        
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

    def get_modem_password(self, mac_wan):
        p = os.popen("pass.exe " + mac_wan).read()
        pass_ = str(p.replace("passwd:", "").replace(
            " ", "").replace("\n", ""))
        return pass_

    def get_modem_info(self):
        url = 'http://192.168.1.1/devinfo.html'
        r = self.session.get(url)
        # print(r.text)
        info = r.content.decode('utf-8').split('\n')
        dev_name = ''
        firmware = ''
        power = ''
        for line in info:
            if 'dev_name =' in line and 'var' not in line:
                dev_name += line
            if 'sw_ver = ' in line and 'var' not in line:
                firmware += line
            if 'rxpower=' in line and 'var' not in line:
                power += line
        dev_name = dev_name.replace(';', '').replace(
            'dev_name = ', '').replace('"', '').strip()
        firmware = firmware.replace(';', '').replace(
            'sw_ver = ', '').replace('"', '').strip()
        power = power.replace('rxpower=', '').replace(';', '').replace('"', '')
        try:
            power = str(round(float(power) / 500 - 30, 2))
        except:
            power = '---'
        return dev_name, firmware, power

    def update_firmware(self, firmware):
        file_upload = {
            'up_img': open(firmware, 'rb')
        }
        value = {
            'XWebPageName': 'upgrade'
        }
        url = 'http://192.168.1.1/GponForm/upgrade_XForm'
        r = self.session.post(url, files=file_upload, data=value)
        return r.status_code

    def login_modem(self):
        url = 'http://192.168.1.1/GponForm/LoginForm'
        values = {
            "XRanID": self.dev_username + self.dev_password + "index",
            "XWebPageName": "index",
            "username": self.dev_username,
            "password": self.dev_password
        }
        r = self.session.post(url, data=values)
        
        return r.status_code

    def config_wifi_24g_basic(self):
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

    def config_wifi_24g_ssid(self):
        url = 'http://192.168.1.1/GponForm/wifissid_XForm'
        values = {
            "XWebPageName": "wifissid",
            "ssid_list": "0",
            "ssid_state": "1",
            "ssid_network_name": self.wifi_24_ssid,
            "ssid_broadcast": "1",
            "wmm": "1"
        }
        r = self.session.post(url, data=values)
        return r.status_code
 
    def config_wifi_24g_secutity(self):
        url = 'http://192.168.1.1/GponForm/wifisecu_XForm'
        values = {
            "XWebPageName": "wifi5secu",
            "ssid_list": "0",
            "select_security_mode": "2",
            "encryption_wpa_type": "0",
            "security_wpa_key": self.wifi_24_pass,
            "encryption_wep_type": "0",
            "security_wep_key": "",
            "server": "",
            "port": "",
            "key": "",
            "interval": ""
        }
        r = self.session.post(url, data=values)
        return r.status_code

    def config_wifi_5g_basic(self):
        url = 'http://192.168.1.1/GponForm/wifi5basic_XForm'
        values = {
            "XWebPageName": "wifi5basic",
            "wireless_radio": "1",
            "wifi_mode": self.wifi_5_mode,
            "channel_bandwidth": self.wifi_5_bandwidth,
            "country": "0",
            "channel": self.wifi_5_channel,
            "power_level": "0",
            "max_clients": "5",
            "wifi_multicast": "1"
        }
        r = self.session.post(url, data=values)
        return r.status_code

    def config_wifi_5g_ssid(self):
        url = 'http://192.168.1.1/GponForm/wifi5ssid_XForm'
        values = {
            "XWebPageName": "wifi5ssid",
            "ssid_list": "0",
            "ssid_state": "1",
            "ssid_network_name": self.wifi_5_ssid,
            "ssid_broadcast": "1",
            "wmm": "1"
        }
        r = self.session.post(url, data=values)
        return r.status_code

    def config_wifi_5g_secutity(self):
        url = 'http://192.168.1.1/GponForm/wifi5secu_XForm'
        values = {
            "XWebPageName": "wifi5secu",
            "ssid_list": "0",
            "select_security_mode": "2",
            "encryption_wpa_type": "0",
            "security_wpa_key": self.wifi_5_pass,
            "encryption_wep_type": "0",
            "security_wep_key": "",
            "server": "",
            "port": "",
            "key": "",
            "interval": ""
        }
        r = self.session.post(url, data=values)
        return r.status_code

    def config_wan(self):
        url = 'http://192.168.1.1/GponForm/wan_XForm'
        values = {
            "XWebPageName": "wan",
            "wan_list": "0",
            "wan_en": "1",
            "internet": "4",
            "tr069": "2",
            "iptv": "8",
            "ip_ver": "2",
            "ip_mode": "1",
            "mtu": "1492",
            "nat": "1",
            "metric": "1",
            "ppp_user": self.wan_account,
            "ppp_pass": self.wan_password,
            "ppp_mode": "0",
            "static_ip": "",
            "static_mask": "",
            "static_gw": "",
            "ipv6_static_addr": "",
            "ipv6_static_wanplen": "",
            "dnswr": "0",
            "dns1": "0.0.0.0",
            "dns2": "0.0.0.0",
            "ipv6_dnswr": "0",
            "ipv6_dns1": "",
            "ipv6_dns2": "",
            "rd6_en": "0",
            "rd6_opt": "0",
            "rd6_manual_prefix_val": "",
            "rd6_manual_prefix_length_val": "0",
            "rd6_manual_ipv4mask_length_val": "0",
            "rd6_manual_border_addr_val": "0.0.0.0",
            "dslite_en": "0",
            "dslite_mode": "0",
            "dslite_aftraddr": "",
            "ipv6_ad_mode": "2",
            "ipv6_ad_static": "",
            "ipv6_pd_mode": "16",
            "ipv6_pd_static": "",
            "ipv6gw": ""
        }
        r = self.session.post(url, data=values)
        return r.status_code

class AC1000F():
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

    def login(self):
        self.session.cookies.set('uid', self.username)
        self.session.cookies.set('psw', self.password)
        url = "http://192.168.1.1/cgi-bin/requestFromLoginPage"
        try:
            r = self.session.get(url)
            return r.status_code
        except:
            return 401

    def logout(self):
        self.session.cookies.clear()
        self.session.cookies.set('logout', '1')
        data = {
            'StatusActionFlag': ''
        }
        url = 'http://192.168.1.1/cgi-bin/status.asp'
        try:
            r = self.session.post(url, data=data)
        except:
            pass
        finally:
            return r.status_code
        
    def get_device_info(self):
        return 'AC1000F', '---', '---'

    def config_wifi_24g(self):
        data = {
            "isWPSSupported": "1",
            "WscV2Support": "0",
            "BasicRate_Value1": "15",
            "BasicRate_Value2": "3",
            "BasicRate_Value3": "351",
            "CountryRegion0": "0",
            "CountryRegion1": "1",
            "CountryRegion2": "2",
            "CountryRegion3": "3",
            "CountryRegion5": "5",
            "CountryRegion6": "6",
            "CountryRegionABand0": "0",
            "CountryRegionABand1": "1",
            "CountryRegionABand2": "2",
            "CountryRegionABand3": "3",
            "CountryRegionABand4": "4",
            "CountryRegionABand5": "5",
            "CountryRegionABand6": "6",
            "CountryRegionABand7": "7",
            "CountryRegionABand8": "8",
            "CountryRegionABand9": "9",
            "CountryRegionABand10": "10",
            "CountryRegionABand11": "11",
            "HTMCSAUTO": "33",
            "HTBW": "0",
            "WPSConfigured": "2",
            "WpsConfModeAll": "7",
            "WpsConfModeNone": "0",
            "WpsStart": "0",
            "WpsOOB": "0",
            "isInWPSing": "0",
            "WpsGenerate": "0",
            "Is11nMode": "1",
            "is11nSpecComply": "N/A",
            "isWPA2PreAuthSupported": "N/A",
            "Wlan_HTBW40M": "0",
            "ExtChannFlag": "1",
            "isAuthenTypeSupported": "0",
            "isDot1XSupported": "0",
            "isDot1XEnhanceSupported": "0",
            "wlan_VC": "0",
            "BssidNum": "4",
            "CountryName": "VIETNAM",
            "hCountryRegion": "1",
            "hRekeyMethod": "TIME",
            "isWDSSupported": "1",
            "WDS_EncrypType_NONE": "NONE",
            "WDS_EncrypType_WEP": "WEP",
            "bharti_ssid2": "0",
            "isPerSSIDSupport": "1",
            "RTDEVICE": "7615",
            "WLanITxBfEn": "N/A",
            "WLanETxBfEnCond": "N/A",
            "WLanETxBfIncapable": "N/A",
            "WEP_Key": "0",
            "wlan_APenable": "1",
            "Bandsteering_Selection": "1",
            "BeaconInterval": "100",
            "RTSThreshold": "2347",
            "FragmentThreshold": "2346",
            "DTIM": "1",
            "WirelessMode": self.wifi_24_mode,
            "TxPower": "100",
            "maxStaNum": "31",
            "StationNum": "0",
            "Countries_Channels": "VIETNAM",
            "Channel_ID": self.wifi_24_channel,
            "WLANChannelBandwidth": "0",
            "WLANGuardInterval": "0",
            "WLANMCS": "33",
            "SSID_INDEX": "0",
            "ESSID_Enable_Selection": "1",
            "ESSID": self.wifi_24_ssid,
            "ESSID_HIDE_Selection": "0",
            "WMM_Selection": "1",
            "WEP_Selection": "WPAPSKWPA2PSK",
            "wlanWEPFlag": "3",
            "WEP_TypeSelection1": "WEPAuto",
            "DefWEPKey3": "1",
            "WEP_Key13": "",
            "WEP_Key23": "",
            "WEP_Key33": "",
            "WEP_Key43": "",
            "WEP_TypeSelection2": "WEPAuto",
            "DefWEPKey4": "1",
            "WEP_Key14": "",
            "WEP_Key24": "",
            "WEP_Key34": "",
            "WEP_Key44": "",
            "TKIP_Selection4": "TKIPAES",
            "PreSharedKey1": self.wifi_24_pass,
            "keyRenewalInterval1": "10",
            "TKIP_Selection5": "TKIPAES",
            "PreSharedKey2": self.wifi_24_pass,
            "keyRenewalInterval2": "10",
            "TKIP_Selection6": "TKIPAES",
            "PreSharedKey3": self.wifi_24_pass,
            "keyRenewalInterval3": "10",
            "UseWPS_Selection": "1",
            "WPSMode_Selection": "1",
            "WPSPinMode_Selection": "1",
            "WPSEnrolleePINCode": "",
            "WLAN_WDS_Active": "0",
            "WLAN_FltActive": "0",
            "WLAN_FltAction": "1",
            "Mac_filter_flag": "0",
            "Mac_filter_id": "0",
            "delnum": "",
            "unsetmacaddr": "",
            "LAN_Device_mac_select": "0",
            "LAN_Manual_Mac": "",
            "TxStream_Action": "2",
            "RxStream_Action": "2",
            "LeaseNum": "0",
            "CountryChange": "1",
            "ChangeCountry": "0",
            "AutoChannel": "0",
        }
        if self.wifi_24_bandwidth == '0':
            # 20M
            data['Wlan_HTBW40M'] = '0'
            data['WLANChannelBandwidth'] = '0'

        elif self.wifi_24_bandwidth == '1':
            # 40M
            data['Wlan_HTBW40M'] = '0'
            data['WLANChannelBandwidth'] = '1'

        elif self.wifi_24_bandwidth == '2':
            # auto
            data['Wlan_HTBW40M'] = '1'
            data['WLANChannelBandwidth'] = '1'

        url = 'http://192.168.1.1/cgi-bin/home_wireless.asp'
        try:
            r = self.session.post(url, data=data)
            return r.status_code
        except:
            return -1

    def config_wifi_5g(self):
        data = {
            "isWPSSupported": "1",
            "WscV2Support": "0",
            "BasicRate_Value1": "15",
            "BasicRate_Value2": "3",
            "BasicRate_Value3": "351",
            "CountryRegionABand0": "0",
            "CountryRegionABand1": "1",
            "CountryRegionABand2": "2",
            "CountryRegionABand3": "3",
            "CountryRegionABand4": "4",
            "CountryRegionABand5": "5",
            "CountryRegionABand6": "6",
            "CountryRegionABand7": "7",
            "CountryRegionABand8": "8",
            "CountryRegionABand9": "9",
            "CountryRegionABand10": "10",
            "CountryRegionABand11": "11",
            "CountryRegion0": "0",
            "CountryRegion1": "1",
            "CountryRegion2": "2",
            "CountryRegion3": "3",
            "CountryRegion5": "5",
            "CountryRegion6": "6",
            "HTMCSAUTO": "33",
            "HTBW": "0",
            "VHTBW": "0",
            "RTDEVICE": "7615",
            "WEP_Key": "0",
            "VHTSec80Channel": "0",
            "WLan11acITxBfEn": "0",
            "WLan11acETxBfEnCond": "0",
            "WLan11acETxBfIncapable": "1",
            "WPSConfigured": "2",
            "WpsConfModeAll": "7",
            "WpsConfModeNone": "0",
            "WpsStart": "0",
            "WpsOOB": "0",
            "isInWPSing": "0",
            "WpsGenerate": "0",
            "Is11nMode": "1",
            "Is11acMode": "1",
            "Wlan_HTBW40M": "0",
            "ExtChannFlag": "0",
            "isAuthenTypeSupported": "0",
            "isDot1XSupported": "0",
            "isDot1XEnhanceSupported": "0",
            "BssidNum": "4",
            "CountryName": "VIETNAM",
            "hCountryRegionABand": "0",
            "hRekeyMethod": "TIME",
            "isWDSSupported": "1",
            "WDS_EncrypType_NONE": "NONE",
            "WDS_EncrypType_WEP": "WEP",
            "bharti_ssid2": "0",
            "isPerSSIDSupport": "1",
            "wlan_APenable": "1",
            "BeaconInterval": "100",
            "RTSThreshold": "2347",
            "FragmentThreshold": "2346",
            "DTIM": "1",
            "WirelessMode": self.wifi_5_mode,
            "TxPower": "100",
            "maxStaNum": "31",
            "StationNum": "0",
            "Countries_Channels": "VIETNAM",
            "Channel_ID": self.wifi_5_channel,
            "LeaseNum": "0",
            "WLANChannelBandwidth": "0",
            "WLANGuardInterval": "0",
            "WLANMCS": "33",
            "WLan11acVHTChannelBandwidth": "1",
            "WLan11acTxBeamForming": "0",
            "WLan11acVHTGuardInterval": "0",
            "SSID_INDEX": "0",
            "ESSID_Enable_Selection": "1",
            "ESSID": self.wifi_5_ssid,
            "ESSID_HIDE_Selection": "0",
            "WMM_Selection": "1",
            "WEP_Selection": "WPAPSKWPA2PSK",
            "wlanWEPFlag": "3",
            "WEP_TypeSelection1": "WEPAuto",
            "DefWEPKey3": "1",
            "WEP_Key13": "",
            "WEP_Key23": "",
            "WEP_Key33": "",
            "WEP_Key43": "",
            "WEP_TypeSelection2": "WEPAuto",
            "DefWEPKey4": "1",
            "WEP_Key14": "",
            "WEP_Key24": "",
            "WEP_Key34": "",
            "WEP_Key44": "",
            "TKIP_Selection4": "TKIPAES",
            "PreSharedKey1": self.wifi_5_pass,
            "keyRenewalInterval1": "3600",
            "TKIP_Selection5": "TKIPAES",
            "PreSharedKey2": self.wifi_5_pass,
            "keyRenewalInterval2": "3600",
            "TKIP_Selection6": "TKIPAES",
            "PreSharedKey3": self.wifi_5_pass,
            "keyRenewalInterval3": "3600",
            "UseWPS_Selection": "1",
            "WPSMode_Selection": "1",
            "WPSPinMode_Selection": "1",
            "WPSEnrolleePINCode": "",
            "WLAN_WDS_Active": "0",
            "WLAN_FltActive": "0",
            "WLAN_FltAction": "1",
            "Mac_filter_flag": "0",
            "Mac_filter_id": "0",
            "delnum": "",
            "unsetmacaddr": "",
            "LAN_Device_mac_select": "0",
            "LAN_Manual_Mac": "",
            "TxStream_Action": "2",
            "RxStream_Action": "2",
            "wlan_Calibration": "1",
            "Calibrationflag": "0",
            "CountryChange": "1",
            "ChangeCountry": "0",
            "AutoChannel": "0",
        }
        if self.wifi_5_bandwidth == '0':
            # 20M
            data['ExtChannFlag'] = '1'
            data['WLANChannelBandwidth'] = '0'
            data['WLANExtensionChannel'] = '1'
        elif self.wifi_5_bandwidth == '1':
            # 40M
            data['Wlan_HTBW40M'] = '0'
            data['WLANChannelBandwidth'] = '1'
        elif self.wifi_5_bandwidth == '2':
            # auto
            data['Wlan_HTBW40M'] = '1'
            data['WLANChannelBandwidth'] = '1'

        url = 'http://192.168.1.1/cgi-bin/home_wireless_5g.asp'
        try:
            r = self.session.post(url, data=data)
            return r.status_code
        except:
            return -1

    def config_wan(self):
        data = {
            "hidEncapFlag": "0",
            "hidEncap": "0",
            "disLanDHCP": "0",
            "enableLanDHCP": "1",
            "isIPv6Supported": "1",
            "DynIPv6Enable_flag": "N/A",
            "PPPDHCPv6Enable_Flag": "N/A",
            "PPPDHCPv6Mode_Flag": "0",
            "IPv6PD_Flag": "Yes",
            "DHCP6SMode_Flag": "0",
            "IPVERSION_IPv4": "IPv4",
            "wanTransFlag": "0",
            "wanBarrierFlag": "0",
            "ptm_VC": "8",
            "wanVCFlag": "3",
            "service_num_flag": "0",
            "wanSaveFlag": "1",
            "vciCheckFlag": "0",
            "wanEncapFlag": "0",
            "DSLITE_MANUAL_MODE": "1",
            "IPVersion_Flag": "0",
            "is8021xsupport": "0",
            "isDSLITESupported": "0",
            "wan_8021q": "1",
            "disp_wan_8021q": "1",
            "DefaultWan_Active": "No",
            "DefaultWan_ISP": "3",
            "DefaultWan_IPVERSION": "IPv4",
            "DefaultWan_MLDproxy": "N/A",
            "ipv6SupportValue": "0",
            "UserMode": "0",
            "wan_certificate": "N/A",
            "wan_CA": "N/A",
            "wan_HiddenBiDirectionalAuth": "N/A",
            "IPv6PrivacyAddrsSupportedFlag": "N/A",
            "wan_TransMode": "Fiber",
            "wan_VC": "0",
            "wan_VCStatus": "Yes",
            "ipVerRadio": "IPv4/IPv6",
            "wanTypeRadio": "2",
            "wan_dot1q": "No",
            "wan_mvlan": "-1",
            "wan_NAT": "Enable",
            "wan_status": "Disabled",
            "wan_eapIdentity": "",
            "wan_authentication": "on",
            "wan_BridgeInterface0": "Yes",
            "WAN_DefaultRoute0": "Yes",
            "wan_TCPMTU0": "0",
            "wan_NAT0": "Enable",
            "wan_RIP0": "RIP1",
            "wan_RIP_Dir0": "None",
            "wan_IGMP0": "No",
            "DynIPv6EnableRadio": "1",
            "PPPIPv6PDRadio0": "Yes",
            "wan_MLD0": "No",
            "DSLITEEnableRadio0": "No",
            "DSLITEModeRadio0": "0",
            "DSLITEAddr0": "N/A",
            "wan_BridgeInterface1": "Yes",
            "WAN_DefaultRoute1": "Yes",
            "wan_TCPMTU1": "0",
            "wan_StaticIPaddr1": "",
            "wan_StaticIPSubMask1": "",
            "wan_StaticIpGateway1": "",
            "wan_RIP_Dir1": "None",
            "wan_IGMP1": "No",
            "wan_IPv6Addr": "",
            "wan_IPv6Prefix": "",
            "wan_IPv6DefGw": "",
            "wan_IPv6DNS1": "",
            "wan_IPv6DNS2": "",
            "wan_MLD1": "No",
            "DSLITEEnableRadio1": "No",
            "DSLITEAddr1": "",
            "wan_PPPUsername": self.wan_account,
            "TTNETGuiSupport": "0",
            "wan_PPPPassword": self.wan_password,
            "wan_BridgeInterface2": "Yes",
            "wan_ConnectSelect": "Connect_Keep_Alive",
            "pppoe_relay": "No",
            "wan_TCPMSS": "0",
            "wan_IPTV": "No",
            "WAN_DefaultRoute2": "Yes",
            "wan_PPPGetIP": "Dynamic",
            "dnsTypeRadio": "0",
            "wan_RIP2": "RIP1",
            "wan_RIP_Dir2": "None",
            "wan_TCPMTU2": "0",
            "wan_IGMP2": "No",
            "PPPIPv6ModeRadio": "0",
            "PPPIPv6PDRadio2": "Yes",
            "wan_MLD2": "No",
            "DSLITEEnableRadio2": "No",
            "DSLITEModeRadio2": "0",
            "DSLITEAddr2": "",
            "isPPPAuthen": "N/A",
            "isWanTagChk": "N/A",
            "isdot1pSupport": "N/A",
            "isTPIDSupported": "N/A",
            "DefaultDmz_Active": "No",
            "DefaultDmz_HostIP": "0.0.0.0"
        }
        url = 'http://192.168.1.1/cgi-bin/home_wan.asp'
        try:
            r = self.session.post(url, data=data)
            return r.status_code
        except:
            return -1

    def update_firmware(self, firmware):
        file_upload = {
            'tools_FW_UploadFile': open(firmware, 'rb')
        }
        value = {
            'postflag': '1',
            'HTML_HEADER_TYPE': '2'
        }

        url = 'http://192.168.1.1/cgi-bin/tools_update.asp'
        r = self.session.post(url, files=file_upload, data=value)
        return r.status_code

class AC1000Z:
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
        

    def get_password(self):
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
        # print(info)
        for line in info:
            if 'dev_name =' in line and 'var' not in line:
                dev_name += line
            if 'sw_ver = ' in line and 'var' not in line:
                firmware += line
            if 'rxpower=' in line and 'var' not in line:
                power += line
        dev_name = dev_name.replace(';', '').replace(
            'dev_name = ', '').replace('"', '').strip()
        firmware = firmware.replace(';', '').replace(
            'sw_ver = ', '').replace('"', '').strip()
        power = power.replace('rxpower=', '').replace(';', '').replace('"', '')
        try:
            power = str(round(float(power) / 500 - 30, 2))
        except:
            power = '---'
        return dev_name, firmware, power

    def login(self):
        url = 'http://192.168.1.1/GponForm/LoginForm'
        values = {
            "XRanID": self.username + self.password + "index",
            "XWebPageName": "index",
            'XNonce': '',
            "username": self.username,
            "password": self.password
        }
        r = self.session.post(url, data=values)
        print(r.status_code)
        return r.text
    def logout(self):
        pass
    def config_24G(self):
        pass
    def config_5G(self):
        pass
    def config_wan(self):
        pass
    def update_firmware(self):
        pass
if __name__ == '__main__':
    modem = ConfigModem()
    mac_lan, mac_wan = modem.get_gateway_mac(ip = '192.168.1.1')
    print(mac_lan, mac_wan)
    p = os.popen("pass.exe " + mac_wan).read()
    pass_ = str(p.replace("passwd:", "").replace(
            " ", "").replace("\n", ""))
    print(pass_)
    rg6w = G97RG_Model(dev_username='admin', dev_password = pass_)
    login_status = rg6w.login_modem()
    print(login_status)
    status = 0
    if login_status == 200:
    
        dev_name, firmware, power = rg6w.get_modem_info()
        print(dev_name, firmware, power)
        status = rg6w.config_wifi_24g_basic()
        print(status)
        

    # gr97 = G97RG_Model('admin', pass_)
    # login_code = gr97.login_modem()
    # print(login_code)
    # if login_code == 200:
    #     info = gr97.get_modem_info()
    #     print(info)
    # print(login)
    # p = os.popen("pass.exe " + mac_wan).read()
    # pass_ = str(p.replace("passwd:", "").replace(
    #         " ", "").replace("\n", ""))
    # # print(pass_)
    # ac1000f = AC1000F('admin', '9402B5CED0')
    # login = ac1000f.login()
    # print("Check login: ", login)

    # # # print(password)
    # if login == 200:
    #     check = ac1000f.config_wifi_24g()
    #     print("check 2.4G config: ", check)
    #     check = ac1000f.config_wifi_5g()
    #     print("check 5G config: ", check)
    #     check = ac1000f.config_wan()
    #     print("check wan config: ", check)
    #     check = ac1000f.logout()
    #     print("Check logout: ", check)
        
        
        


    # login = g97rg_model.login_modem()
    # if login == 200:
        # dev_name, firmware, power = ac1000f.get_modem_info()
        # print(dev_name, firmware, power)

    # a = 'rxpower="-4256";'
    # power = a.replace('rxpower=', '').replace(';', '').replace('"', '')
    # try:
    #     power = str(round(float(power) / 500 - 30, 2))
    # except:
    #     power = '---'
    # print(power)
    # a = shutil.copy(txtName, os.path.join(os.environ["HOMEPATH"], "Desktop"))
    # print(a)