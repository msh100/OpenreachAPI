import requests
import re
import base64
from Crypto.Cipher import AES
from datetime import datetime
import random
import string
import json

class ORChecker:
    def __init__(
        self,
        basicAuth=None,
        AESKey=None,
        APIAddress=None,
        baseURL="https://www.broadbandchecker.btwholesale.com",
        ORJavascript=None,
        useKnownKeys=True,
    ):
        if useKnownKeys:
            self.set_known_keys()
        else:
            self.basicAuth = basicAuth
            self.AESKey = AESKey
            self.APIAddress = APIAddress

        self._ORJavascript = ORJavascript
        self._baseURL = baseURL
        self.newTrackingHeader()


    @property
    def ORJavascript(self):
        # Within the main page there's a JS file which contains some essential
        # keys. Request the Javascript file and extract these keys is they have
        # not been provided. We can also specify useKnownKeys to bypass all of
        # this logic using the last known working data.
        if not self._ORJavascript:
            baseRequest = requests.get(self.baseURL)

            jsExtractRegex = 'main\.([0-9a-f])+\.js'
            jsPath = re.search(jsExtractRegex, baseRequest.text).group(0)
            jsRequest = requests.get(f'{self.baseURL}/{jsPath}')
            self._ORJavascript = jsRequest.text

        return self._ORJavascript


    @property
    def basicAuth(self):
        if not self._basicAuth:
            basicRegex = 'Basic ([A-Za-z0-9=])+'
            self.basicAuth = re.search(basicRegex,
                self.ORJavascript).group(0)

        return self._basicAuth

    @basicAuth.setter
    def basicAuth(self, value):
        self._basicAuth = value


    @property
    def AESKey(self):
        if not self._AESKey:
            AESFetchRegex = 'enc\.Base64\.parse\(\"([^\"]+)\"\)'
            AESKey = re.search(AESFetchRegex, self.ORJavascript)
            self.AESKey = base64.b64decode(AESKey.group(1))

        return self._AESKey

    @AESKey.setter
    def AESKey(self, value):
        self._AESKey = value
        self.cipher = AES.new(self.AESKey, AES.MODE_ECB)
        self.decipher = AES.new(self.AESKey, AES.MODE_ECB)


    @property
    def APIAddress(self):
        if not self._APIAddress:
            APIRegex = 'this\.telnoUrl=\"([^\"]+)\"'
            self.APIAddress = re.search(
                APIRegex, self.ORJavascript).group(1)

        return self._APIAddress

    @APIAddress.setter
    def APIAddress(self, value):
        self._APIAddress = value


    @property
    def trackingHeader(self):
        return self._trackingHeader

    @trackingHeader.setter
    def trackingHeader(self, value):
        self._trackingHeader = value
        trackingHash = self.cipher.encrypt(
            self.Pkcs7_padd(value + self.random_string(6))
        )
        trackingHash = base64.b64encode(trackingHash).decode('ascii')
        self.trackingHash = f'bbac{trackingHash}'


    @property
    def baseURL(self):
        return self._baseURL


    @property
    def defaultHeaders(self):
        return {
            "APIGW-Tracking-Header": self.trackingHeader,
            "AuthTrackCap": self.trackingHash,
            "Authorization": self.basicAuth,
            "requestType": "request1",
            "Origin": self.baseURL,
        }


    def newTrackingHeader(self):
        # Replicate the randomness used by tracking.
        nowTimestamp = datetime.now().strftime("%d%m%Y%H%M%S")
        self.trackingHeader = self.random_string(8) + nowTimestamp


    @staticmethod
    def Pkcs7_padd(m):
        return m+chr(16-len(m)%16)*(16-len(m)%16)


    @staticmethod
    def random_string(length):
        alphanum = string.ascii_lowercase + string.digits
        return ''.join(random.choice(alphanum) for _ in range(length))


    @staticmethod
    def strip_excess(string):
        # The returned value often has random garbage after the json closing
        # bracket. Just discard everything until we hit a closing bracket.
        while string[-1] != "}":
            string = string[:-1]
        return string


    def set_known_keys(self):
        self.APIAddress = ( 'https://api.wholesale.bt.com'
                '/bt-wholesale/v1/broadband/coverage/anonymous' )
        self.AESKey = b'GhB$skWWTrE27e=('
        self.basicAuth = ( 'Basic MjFuZ0dHNks0bk9NY3gybEpzWkp'
                'WUFZZQXlZdTJIV3Y6Vjd1M1FQT2xITXF2TFRKbA==' )


    def api_request(self, requestHeaders, asJSON):
        # Request from the API. This data is returned base64 encoded and AES
        # ECB 128 encrypted. We need to decrypt this data with AESKey and parse
        # it as JSON.
        APIData = requests.get(
            self.APIAddress,
            headers={
                **requestHeaders,
                **self.defaultHeaders,
            }).text.strip('"')
        APIData = base64.b64decode(APIData)
        APIData = self.decipher.decrypt(APIData).strip()
        jsonOutput = self.strip_excess(APIData.decode("UTF-8"))

        if asJSON:
            return jsonOutput
        return json.loads(jsonOutput)


    def query_address(self, postCode, houseNumber, asJSON=False):
        requestHeaders={
            "postCode": postCode,
            "buildingNumber": houseNumber,
        }
        return self.api_request(requestHeaders, asJSON)
