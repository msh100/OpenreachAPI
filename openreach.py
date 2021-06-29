import requests
import re
import base64
from Crypto.Cipher import AES
from datetime import datetime
import random
import string

class ORChecker:
    def __init__(self):
        self.baseURL = "https://www.broadbandchecker.btwholesale.com"
        baseRequest = requests.get(self.baseURL)

        # Within the main page there's a JS file which contains some essential
        # keys. Request the Javascript file and extract these keys.
        jsPath = re.search('main\.([0-9a-f])+\.js', baseRequest.text).group(0)
        jsRequest = requests.get(f'{self.baseURL}/{jsPath}')

        basicRegex = 'Basic ([A-Za-z0-9=])+'
        self.basicPassword = re.search(basicRegex, jsRequest.text).group(0)

        AESKey = re.search('enc\.Base64\.parse\(\"([^\"]+)\"\)', jsRequest.text)
        AESKey = base64.b64decode(AESKey.group(1))
        self.cipher = AES.new(AESKey, AES.MODE_ECB)
        self.decipher = AES.new(AESKey, AES.MODE_ECB)

        APIRegex = 'this\.telnoUrl=\"([^\"]+)\"'
        self.APIAddress = re.search(APIRegex, jsRequest.text).group(1)

        # Replicate the randomness used by tracking.
        nowTimestamp = datetime.now().strftime("%d%m%Y%H%M%S")
        self.trackingHeader = self.random_string(8) + nowTimestamp
        trackingHash = self.cipher.encrypt(
            self.Pkcs7_padd(self.trackingHeader + self.random_string(6))
        )
        trackingHash = base64.b64encode(trackingHash).decode('ascii')
        self.trackingHash = f'bbac{trackingHash}'


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


    def query(self, postCode, houseNumber):
        # Request from the API. This data is returned base54 encoded and AES
        # ECB 128 encrypted. We need to decrypt this data with AESKey and parse
        # it as JSON.
        wholesaleData = requests.get(
            self.APIAddress,
            headers={
                "APIGW-Tracking-Header": self.trackingHeader,
                "postCode": postCode,
                "Authorization": self.basicPassword,
                "AuthTrackCap": self.trackingHash,
                "requestType": "request1",
                "buildingNumber": houseNumber,
                "Origin": self.baseURL,
            }).text.strip('"')
        wholesaleData = base64.b64decode(wholesaleData)
        wholesaleData = self.decipher.decrypt(wholesaleData).strip()

        return self.strip_excess(wholesaleData.decode("UTF-8"))
