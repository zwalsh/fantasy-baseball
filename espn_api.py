import requests
import json
import os


class EspnApi:
    LOGIN_URL = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/guest/login?langPref=en-US"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def session_file_name(self):
        return "espn_s2_{u}.txt".format(u=self.username)

    @staticmethod
    def api_key():
        key_url = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/api-key?langPref=en-US"
        resp = requests.post(key_url)
        return "APIKEY " + resp.headers["api-key"]

    def login(self):
        login_payload = {
            "loginValue": self.username,
            "password": self.password
        }
        login_headers = {
            "authorization": EspnApi.api_key(),
            "content-type": "application/json",
        }
        print("Logging in...")
        resp = requests.post(EspnApi.LOGIN_URL, data=json.dumps(login_payload), headers=login_headers)
        key = resp.json().get('data').get('s2')
        print("Logged in.")
        cache_file = open(self.session_file_name(), "w+")
        cache_file.truncate()
        cache_file.write(key)
        return key

    def key(self):
        if os.path.isfile(self.session_file_name()):
            with open(self.session_file_name(), "r") as file:
                stored_key = file.read()
                if len(stored_key) > 0:
                    return stored_key
        return self.login()

    def espn_request(self, url):
        k = self.key()
        r = requests.get(url, cookies={"espn_s2": k})
        if r.status_code == 401:
            self.login()
            return self.espn_request(url)
        return r
