# Openreach API

A library and CLI to query the Openreach wholesale API.


## Example usage

```bash
$ python3 cli.py -n 10 -p SW1A2AA
{
    "addressMismatch": true,
    "addressObjectList": [
        {
            "address": {
                "districtCode": "WR",
                "exchangeGroupCode": "WHI",
                "location": null,
                "qualifier": "Gold",
...
```

```python
from openreach import ORChecker

checker = ORChecker()
query = checker.query("SW1A2AA", "10")
data = json.loads(query)
```
