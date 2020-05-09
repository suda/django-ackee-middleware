import pytest
from ackee.middleware import TrackerMiddleware

class TestMiddleware():
    class TestInitialization():
        def test_throws_when_misconfigured(self):
            pass

    class TestSending():
        def test_returns_response(self):
            pass
        def test_throws_on_error(self):
            pass
    
    class TestParsing():
        def test_returns_list_of_touples(self):
            tracker = TrackerMiddleware("foo")
            result = tracker._parse_accept_language("en-GB,en-US;q=0.9,en;q=0.8")
            assert result == [
                ("en-GB", "1"),
                ("en-US", "0.9"),
                ("en", "0.8"),
            ]
            assert tracker._parse_accept_language() == []
    
    class TestSanitizing():
        tracker = TrackerMiddleware("foo")
        def test_returns_none(self):
            assert self.tracker._sanitize_accept_language("") == None

        def test_returns_first_language(self):
            assert self.tracker._sanitize_accept_language("en-GB,en-US;q=0.9,en;q=0.8") == "en"
    
    class TestIgnoringPaths():
        def test_returns_bool(self):
            pass
    
    class TestProcessingRequest():
        def test_skips_when_dnt(self):
            pass
        
        def test_skips_when_ignored(self):
            pass

        def test_sends_data(self):
            pass

        def test_does_not_throw(self):
            pass