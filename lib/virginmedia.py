import requests
import re
from datetime import datetime
import json

class VMChecker:
    def __init__(
        self,
        APIAddress="https://storeapi.virginmedia.com/api",
        storeAddress="https://store.virginmedia.com/serviceability"
    ):
        self.commonHeaders = {
            "X-Requested-With": "XMLHttpRequest",
        }
        self.APIAddress = APIAddress
        self.storeAddress = storeAddress


    def query_address(self, postCode, houseNumber, asJSON=False):
        time_stamp = int(datetime.now().timestamp())
        session = requests.Session()

        # We need to get some tokens, this is made by an initial calls.
        # Subsequent API calls will succeed.
        # Then we can fetch the postcode to premise ID mapping from the API,
        # from this determine the premise ID to pass to the store.
        session.get(
            f'{self.APIAddress}/getToken?_={time_stamp}',
            headers=self.commonHeaders,
        )
        address_list = session.post(
            f'{self.APIAddress}/checkAddress',
            headers=self.commonHeaders,
            data={"postcode": postCode}
        )
        premise = self.determine_premise(address_list.text, houseNumber)

        # We do not know how to fetch the serviceability data from the public
        # API (if it is even possible). Instead we make a request to the store
        # webservice, passing the premise IDs from the API. We can then extract
        # the JSON object that is supposed to be passed down to the webclient.
        # This is not split into a seperate function as we still need the
        # session (I am not sure why).
        data = session.post(
            self.storeAddress,
            data={
                "siteId": premise['siteId'],
                "premiseId": premise['premiseId'],
            },
        )

        jsExtractRegex = 'var vmStoreJson= ([^;]+);'
        serviceability = re.search(jsExtractRegex, data.text).group(1)

        if asJSON:
            return serviceability
        return json.loads(serviceability)


    # This is unreliable, I have seen like "34 B" for people who have 34B, we
    # should add some script to work this out, the same logic can be used for
    # cityfibre.
    @staticmethod
    def determine_premise(struct, number):
        data = json.loads(struct)
        for premise in data['addressList']:
            if premise['displayAddress'].startswith(f'{number} '):
                return premise
        return dict()
