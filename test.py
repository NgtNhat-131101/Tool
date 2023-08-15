import requests

username = 'admin'
password = '1965815728'
login_url = 'http://192.168.1.1/GponForm/LoginForm'

session = requests.Session()
login_payload = {
    'XRanID': username + password + 'index',
    'XWebPageName': 'index',
    'username': username,
    'password': password
}

login_response = session.post(login_url, data=login_payload)

print(login_response.status_code)
if login_response.status_code == 200:
    print("Successful")


info_url = 'http://192.168.1.1/devinfo.html'
info_response = session.get(info_url)
print(info_response.text)

