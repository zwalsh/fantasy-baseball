import json
import logging
import time

import requests

from espn.espn_session_store import EspnSessionStore


class LoginException(Exception):
    """
    Exception to throw when Login to ESPN was unsuccessful
    """
    pass

LOGGER = logging.getLogger("espn.api.espn_session_provider")


class EspnSessionProvider:
    LOGIN_URL = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/guest/login?langPref=en-US"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session_store = EspnSessionStore()

    @staticmethod
    def api_key():
        key_url = "https://registerdisney.go.com/jgc/v6/client/ESPN-ONESITE.WEB-PROD/api-key?langPref=en-US"
        resp = requests.post(key_url)
        return "APIKEY " + resp.headers["api-key"]

    def __session_key(self):
        return f"espn_s2_{self.username}.txt"

    def __login(self):
        login_payload = {
            "loginValue": self.username,
            "password": self.password
        }
        login_headers = {
            "authorization": EspnSessionProvider.api_key(),
            "content-type": "application/json",
        }
        LOGGER.info("logging into ESPN for %(user)s...", {"user": self.username})
        start = time.time()
        resp = requests.post(EspnSessionProvider.LOGIN_URL, data=json.dumps(login_payload), headers=login_headers)
        end = time.time()
        if resp.status_code != 200:
            LOGGER.error("could not log into ESPN: %(msg)s", {"msg": resp.reason})
            LOGGER.error(resp.text)
            raise LoginException
        key = resp.json().get('data').get('s2')
        LOGGER.info("logged in for %(user)s after %(time).3fs", {"user": self.username, "time": end - start})
        return key

    def get_session(self):
        stored_val = self.session_store.retrieve_session(self.__session_key())
        if stored_val:
            LOGGER.info(f"Using stored session for user {self.username}")
            return stored_val
        return self.refresh_session()

    def refresh_session(self):
        session = self.__login()
        self.session_store.store_session(self.__session_key(), session)
        return session
