import requests
import re
from user_agents import parse
from functools import reduce
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class TrackerMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        if not hasattr(settings, "ACKEE_SERVER"):
            raise ImproperlyConfigured("Please set ACKEE_SERVER in settings")
        if not hasattr(settings, "ACKEE_DOMAIN_ID"):
            raise ImproperlyConfigured("Please set ACKEE_DOMAIN_ID in settings")
        if not hasattr(settings, "ACKEE_IGNORED_PATHS"):
            raise ImproperlyConfigured("Please set ACKEE_IGNORED_PATHS in settings")
        self.get_response = get_response

    def _send(self, data):
        url = f"{settings.ACKEE_SERVER}/domains/{settings.ACKEE_DOMAIN_ID}/records"
        response = requests.post(url, json=data)
        if response.status_code == 202:
            return response.json()
        else:
            raise Exception(response.text)

    def _parse_accept_language(self, accept_language=""):
        """Parse and sort the Accept-Language header
        Taken from https://siongui.github.io/2012/10/11/python-parse-accept-language-in-http-request-header/

        Arguments:
            accept_language {str} -- Accept-Language header

        Returns:
            list -- A list of touples containing pairs of language and its priority
        """
        languages = accept_language.split(",")
        locale_q_pairs = []

        if len(languages) == 1 and languages[0] == "":
            return []

        for language in languages:
            if language.split(";")[0] == language:
                # no q => q = 1
                locale_q_pairs.append((language.strip(), "1"))
            else:
                locale = language.split(";")[0].strip()
                q = language.split(";")[1].split("=")[1]
                locale_q_pairs.append((locale, q))

        return locale_q_pairs

    def _sanitize_accept_language(self, accept_language):
        languages = self._parse_accept_language(accept_language)
        if len(languages) == 0:
            return None
        return languages[0][0][:2]

    def _is_ignored_path(self, path):
        for ignore in settings.ACKEE_IGNORED_PATHS:
            if re.match(ignore, path) is not None:
                return True
        return False

    def process_request(self, request):
        # Do not track users who specified DNT header
        if int(request.headers.get("DNT", "0")) == 1:
            return

        if self._is_ignored_path(request.get_full_path()):
            return

        user_agent = parse(request.headers.get("User-Agent", ""))

        data = {
            "siteLocation": request.build_absolute_uri(),
            "siteReferrer": request.headers.get("Referer"),
            "siteLanguage": self._sanitize_accept_language(
                request.headers.get("Accept-Language")
            ),
            "deviceName": user_agent.device.model,
            "deviceManufacturer": user_agent.device.brand,
            "osName": user_agent.os.family,
            "osVersion": user_agent.os.version_string,
            "browserName": user_agent.browser.family,
            "browserVersion": user_agent.browser.version_string,
        }

        try:
            self._send(data)
        except:
            pass
