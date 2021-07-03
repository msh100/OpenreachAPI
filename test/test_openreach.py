import pytest

import sys
sys.path.append(".")
from openreach import ORChecker

with open("test/main.2021-06-30.js", "r") as file:
    ORJavascript = file.read()
ORCheckerLocal = ORChecker(ORJavascript=str(ORJavascript), useKnownKeys=False)
ORCheckerKnownKeys = ORChecker(useKnownKeys=True)
ORCheckerLiveKeys = ORChecker(useKnownKeys=False)

def test_fetch_aes_key():
    fetchAES = ORCheckerLocal.AESKey
    assert fetchAES == b'GhB$skWWTrE27e=('


def test_fetch_basic_auth():
    fetchBasicAuth = ORCheckerLocal.basicAuth
    expected = 'Basic MjFuZ0dHNks0bk9NY3gybEpzWkpWUFZZQXlZdTJIV3Y6Vjd1M1FQT2xITXF2TFRKbA=='
    assert fetchBasicAuth == expected


def test_fetch_api_address():
    fetchAPIAddress = ORCheckerLocal.APIAddress
    expected = 'https://api.wholesale.bt.com/bt-wholesale/v1/broadband/coverage/anonymous'
    assert fetchAPIAddress == expected


def test_strip_excess():
    assert ORCheckerLocal.strip_excess("{asd}asd") == "{asd}"
    assert ORCheckerLocal.strip_excess("{{asd}}asd") == "{{asd}}"
    assert ORCheckerLocal.strip_excess("{asd}\r\n\r\n") == "{asd}"


def test_random_string():
    string1 = ORCheckerLocal.random_string(8)
    string2 = ORCheckerLocal.random_string(8)
    string3 = ORCheckerLocal.random_string(6)
    string4 = ORCheckerLocal.random_string(6)

    assert len(string1) == 8
    assert len(string2) == 8
    assert len(string3) == 6
    assert len(string4) == 6
    assert string1 != string2
    assert string3 != string4


def test_fetch_javascript():
    assert ORCheckerLocal.ORJavascript == ORJavascript
    # TODO: Test an acctual HTTP call?


def test_known_keys_match_live():
    assert ORCheckerKnownKeys.APIAddress == ORCheckerLiveKeys.APIAddress
    assert ORCheckerKnownKeys.basicAuth == ORCheckerLiveKeys.basicAuth
    assert ORCheckerKnownKeys.AESKey == ORCheckerLiveKeys.AESKey


#def test_Pkcs7_padd():
#    # TODO: No idea
