# Openreach API

A library and CLI to query the Openreach wholesale API.


## Example usage

```bash
$ pip install --no-cache-dir -r requirements.txt
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

```bash
$ # With Docker
$ docker build -t msh100/openreachapi .
$ docker run --rm msh100/openreachapi:latest -n 10 -p SW1A2AA
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
