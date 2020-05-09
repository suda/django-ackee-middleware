import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ImproperlyConfigured
from ackee.middleware import TrackerMiddleware
from django.test.utils import override_settings

default_settings = {
    "ACKEE_SERVER": "foo",
    "ACKEE_DOMAIN_ID": 123,
    "ACKEE_IGNORED_PATHS": [],
}


class TestInitialization:
    @patch("ackee.middleware.settings")
    def test_throws_when_no_server(self, settings):
        del settings.ACKEE_SERVER
        with pytest.raises(ImproperlyConfigured):
            TrackerMiddleware("foo")

    @patch("ackee.middleware.settings")
    def test_throws_when_no_domain_id(self, settings):
        del settings.ACKEE_DOMAIN_ID
        with pytest.raises(ImproperlyConfigured):
            TrackerMiddleware("foo")

    @patch("ackee.middleware.settings")
    def test_throws_when_no_ignored_paths(self, settings):
        del settings.ACKEE_IGNORED_PATHS
        with pytest.raises(ImproperlyConfigured):
            TrackerMiddleware("foo")


class TestMiddleware:
    class TestSending:
        @override_settings(**default_settings)
        @patch("ackee.middleware.requests.post")
        def test_returns_response(self, post):
            tracker = TrackerMiddleware("foo")
            response = MagicMock()
            response.status_code = 202
            response.json.side_effect = ["foo"]
            post.side_effect = [response]

            result = tracker._send({"bar": "baz"})
            post.assert_called_once_with("foo/domains/123/records", json={"bar": "baz"})
            assert result == "foo"

        @override_settings(**default_settings)
        @patch("ackee.middleware.requests.post")
        def test_throws_on_error(self, post):
            tracker = TrackerMiddleware("foo")
            response = MagicMock()
            response.status_code = 500
            response.text = "bar"
            post.side_effect = [response]

            with pytest.raises(Exception):
                result = tracker._send({})

    class TestParsing:
        @override_settings(**default_settings)
        def test_returns_list_of_touples(self):
            tracker = TrackerMiddleware("foo")
            result = tracker._parse_accept_language("en-GB,en-US;q=0.9,en;q=0.8")
            assert result == [
                ("en-GB", "1"),
                ("en-US", "0.9"),
                ("en", "0.8"),
            ]
            assert tracker._parse_accept_language() == []

    class TestSanitizing:
        @override_settings(**default_settings)
        def test_returns_none(self):
            tracker = TrackerMiddleware("foo")
            assert tracker._sanitize_accept_language("") == None

        @override_settings(**default_settings)
        def test_returns_first_language(self):
            tracker = TrackerMiddleware("foo")
            assert (
                tracker._sanitize_accept_language("en-GB,en-US;q=0.9,en;q=0.8") == "en"
            )

    class TestIgnoringPaths:
        @override_settings(**default_settings)
        def test_returns_bool(self):
            tracker = TrackerMiddleware("foo")
            assert tracker._is_ignored_path("/foo") == False
            with patch("ackee.middleware.settings.ACKEE_IGNORED_PATHS", "^/bar"):
                assert tracker._is_ignored_path("/bar") == True

    class TestProcessingRequest:
        def setup_method(self, method):
            with override_settings(**default_settings):
                self.tracker = TrackerMiddleware("foo")
                self.tracker._send = MagicMock()
                self.tracker._is_ignored_path = MagicMock()
                self.tracker._is_ignored_path.return_value = False

                self.request = MagicMock()
                self.request.headers = {}

        def test_skips_when_dnt(self):
            self.request.headers = {"DNT": "1"}
            self.tracker.process_request(self.request)
            self.tracker._send.assert_not_called()

        def test_skips_when_ignored(self):
            self.tracker._is_ignored_path.return_value = True
            self.request.get_full_path.return_value = "/foo"

            self.tracker.process_request(self.request)

            self.tracker._is_ignored_path.assert_called_once_with("/foo")
            self.tracker._send.assert_not_called()

        def test_sends_data(self):
            self.request.headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Safari/604.1",
                "Referer": "http://example.com",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            }
            self.request.build_absolute_uri.return_value = "http://foo.bar"
            self.tracker._send.side_effect = Exception()

            self.tracker.process_request(self.request)

            self.tracker._send.assert_called_once_with(
                {
                    "siteLocation": "http://foo.bar",
                    "siteReferrer": "http://example.com",
                    "siteLanguage": "en",
                    "deviceName": "iPhone",
                    "deviceManufacturer": "Apple",
                    "osName": "iOS",
                    "osVersion": "13.3.1",
                    "browserName": "Mobile Safari",
                    "browserVersion": "13.0.5",
                }
            )
