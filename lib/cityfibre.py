import requests
import json
from bs4 import BeautifulSoup

class CFChecker:
    def __init__(
        self,
        baseURL="https://orders.cityfibre.com/ftth/availability-checker",
    ):
        self.baseURL = baseURL


    def get_address_data(self, postCode, houseNumber):
        address_list = requests.post(
            f'{self.baseURL}/postcode',
            data={"postal-code": postCode},
        )
        soup = BeautifulSoup(address_list.text, 'html.parser')

        for address in soup.find_all('option')[1:]:
            addressObj = json.loads(address['value'])
            if addressObj['addressString'].startswith(f'{houseNumber} '):
                return address['value']

        return '{}'


    def query_address(self, postCode, houseNumber, asJSON=False):
        addressData = self.get_address_data(postCode, houseNumber)
        if addressData != '{}':
            status_response = requests.post(
                f'{self.baseURL}/availability',
                data={"address": addressData},
            )
            soup = BeautifulSoup(status_response.text, 'html.parser')
            message = soup.find('h5').text
        else:
            message = ('Could not find property from list for house'
                f' {houseNumber} at {postCode}')

        returnData = {
            "addressData": json.loads(addressData),
            "message": message,
            'serviceable': False,
            'planned': False,
            'success': False,
            'providers': [],
        }

        if returnData['message'].startswith("We're currently planning"):
            returnData.update({
                'planned': True,
                'success': True,
            })
        elif returnData['message'].startswith("Thanks for your interest"):
            returnData.update({
                'success': True,
            })
        elif returnData['message'].startswith("Great news"):
            returnData.update({
                'serviceable': True,
                'planned': True,
                'success': True,
            })
            for provider in soup.find_all('input'):
                if provider.get("name", "") == "ispName":
                    returnData['providers'].append(provider['value'])

        if asJSON:
            return json.dumps(returnData)
        return returnData
