from openreach import ORChecker
import json
import argparse

parser = argparse.ArgumentParser(
    description='Openreach availability checker CLI')

parser.add_argument('-n', '--property-number', required=True,
                    help='The number of the property to check')
parser.add_argument('-p', '--postcode', required=True,
                    help='The postcode of the property to check')
args = parser.parse_args()

checker = ORChecker()
query = checker.query_address(args.postcode, args.property_number, asJSON=True)
data = json.loads(query)

print(json.dumps(data, indent=4, sort_keys=True))
