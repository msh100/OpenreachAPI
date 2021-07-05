from lib import *
import json
import argparse

parser = argparse.ArgumentParser(
    description='Openreach availability checker CLI')

parser.add_argument('-n', '--property-number', required=True,
                    help='The number of the property to check')
parser.add_argument('-p', '--postcode', required=True,
                    help='The postcode of the property to check')

mode = parser.add_mutually_exclusive_group(required=True)
mode.add_argument("--openreach", action="store_true")
mode.add_argument("--virgin-media", action="store_true")
mode.add_argument("--cityfibre", action="store_true")

args = parser.parse_args()

if args.openreach:
    checker = ORChecker()
elif args.virgin_media:
    checker = VMChecker()
elif args.cityfibre:
    checker = CFChecker()
else:
    raise Exception(f'{mode} is an invalid mode of operation')

query = checker.query_address(args.postcode, args.property_number, asJSON=True)
data = json.loads(query)

print(json.dumps(data, indent=4, sort_keys=True))
