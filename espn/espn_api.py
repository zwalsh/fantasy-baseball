import logging
import time

import requests

from espn.sessions.espn_session_provider import EspnSessionProvider

LOGGER = logging.getLogger("espn.api")


class EspnApiException(Exception):
    """
    Exception to throw when a request to the ESPN API failed
    """
    pass


class EspnApi:
    def __init__(self, session_provider):
        """
        Programmatic access to ESPN's (undocumented) API, caching requests that do not need refreshing,
        and automatically fetching a token for the user/password combination.

        :param EspnSessionProvider session_provider: using a username and password, provides and stores session tokens
        """
        self.session_provider = session_provider
        self.cache = dict()

    def espn_request(self, method, url, payload, headers=None, check_cache=True, retries=1):
        if check_cache and url in self.cache.keys():
            return self.cache.get(url)
        LOGGER.info(f"making {method} request to {url} in with headers {headers}")
        start_time = time.time()
        k = self.session_provider.get_session()
        cookies = {"espn_s2": k}
        if method == 'GET':
            r = requests.get(url, headers=headers or {}, cookies=cookies)
        if method == 'POST':
            r = requests.post(url, headers=headers or {}, cookies=cookies, json=payload)
        if r.status_code == 401:
            LOGGER.warning("request denied, logging in again.")
            self.session_provider.refresh_session()
            return self.espn_request(method=method, url=url, payload=payload, headers=headers, check_cache=check_cache)
        if not r.ok:
            LOGGER.error(f"received {r.status_code} {r.reason}: {r.text} in {start_time - time.time():.3f} seconds")
            if retries > 0:
                LOGGER.info(f"retrying request")
                return self.espn_request(method=method, url=url, payload=payload, headers=headers,
                                         check_cache=check_cache, retries=retries - 1)
            else:
                raise EspnApiException(url)
        if r.text is None or r.text == "":
            LOGGER.error(f"the response was blank after {start_time - time.time():.3f} seconds")
            if retries > 0:
                return self.espn_request(method=method, url=url, payload=payload, headers=headers,
                                         check_cache=check_cache, retries=retries - 1)
            else:
                raise EspnApiException(url)
        else:
            end_time = time.time()
            LOGGER.info("finished after %(time).3fs", {"time": end_time - start_time})
        self.cache[url] = r
        return r

    def espn_get(self, url, headers=None, check_cache=True):
        return self.espn_request(method='GET', url=url, payload={}, headers=headers, check_cache=check_cache)

    def espn_post(self, url, payload, headers=None):
        return self.espn_request(method='POST', url=url, payload=payload, headers=headers)
