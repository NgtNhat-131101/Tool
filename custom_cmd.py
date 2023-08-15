import win32com.shell.shell as shell
import subprocess
import shlex
import os
import time
import pywifi
from pywifi import const


def connect_wlan(_ssid, _pass):
    """
    Hàm dùng để kết nối mạng không dây khi biết ssid và password
    """
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    iface.disconnect()
    time.sleep(1)
    assert iface.status() in\
        [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]

    profile = pywifi.Profile()
    profile.ssid = _ssid
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = _pass
    iface.remove_all_network_profiles()
    tmp_profile = iface.add_network_profile(profile)
    time.sleep(10)
    iface.connect(tmp_profile)
    time.sleep(30)
    # print("Connect Successful!!!")
    assert iface.status() == const.IFACE_CONNECTED


def disconnect_wlan():
    """
    Ngắt kết nối mạng không dây
    """
    wifi = pywifi.PyWiFi()

    iface = wifi.interfaces()[0]

    iface.disconnect()
    time.sleep(10)


def set_metric_interface(interface, metric):
    """
    được thiết kế để thiết lập giá trị metric (chỉ số metric)
    cho một giao diện mạng trên hệ điều hành Windows. 
    Metric là một giá trị số được sử dụng trong các mạng TCP/IP
    để xác định đường đi ưu tiên khi gửi dữ liệu qua các giao diện mạng.
    """
    try:
        commands = 'netsh interface ipv4 set interface "%s" metric=%s' % (
            str(interface), str(metric))
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe',
                             lpParameters='/c '+commands)
    except:
        pass


def connect_wifi(ssid, password, interface):
    """
    Mục đích: Kết nối đến mạng WiFi với thông tin SSID (tên mạng WiFi)
    và mật khẩu (_password) cung cấp trên một giao diện (_interface) cụ thể.
    """
    add_wlan_profile(ssid, password)
    time.sleep(5)

    cmd = 'netsh wlan connect name="%s" interface="%s"' % (ssid, interface)
    subprocess.Popen(shlex.split(cmd), creationflags=0x08)
    time.sleep(30)


def disconnect_wifi(interface):
    """
    Mục đích: Ngắt kết nối mạng WiFi với thông tin SSID (tên mạng WiFi) 
    và mật khẩu (_password) cung cấp trên một giao diện (_interface) cụ thể.
    """
    cmd = 'netsh wlan disconnect interface="%s"' % (interface)
    subprocess.Popen(shlex.split(cmd), creationflags=0x08)


def add_wlan_profile(ssid, password):
    """
    Mục đích: Tạo một file XML chứa cấu hình WiFi 
    (gồm thông tin SSID và mật khẩu) để sau đó có thể sử dụng để kết nối đến mạng WiFi.
    """
    with open('wlan_profile.xml', 'r') as f:
        data = f.read()

    data = data.replace('profile_name', ssid).replace('profile_pass', password)

    file_name = 'new_profile.xml'
    with open(file_name, 'w') as f:
        f.write(data)

    profile_path = os.path.join(os.getcwd(), file_name)
    cmd = f'netsh wlan add profile filename="{profile_path}"'

    try:
        process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08)
        _, stderr = process.communicate()
        if process.returncode != 0:
            print(f"Error while adding the Wi-Fi profile: {stderr.decode('utf-8')}")
        else:
            print("Wi-Fi profile added successfully.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")



if __name__ == '__main__':
    connect_wlan('CTS', '0123456789')