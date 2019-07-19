import os
import sys
import requests

### Parse arguments
APIKEY = sys.argv[1]
SYMBOL = sys.argv[2]

#APIKEY = "default"
#SYMBOL = "AMZN"

### Use my key if "default"
if APIKEY == "default":
    with open(os.path.expanduser("~/.secrets/creds")) as f:
        _, _, APIKEY = f.read().split("\n")[:3]

### Derive the query
endpoint = "https://www.alphavantage.co/query"
params = "&".join(("function={}", "symbol={}", "outputsize={}", "datatype={}", "apikey={}"))
call = endpoint + "?" + params.format("TIME_SERIES_DAILY_ADJUSTED",
    SYMBOL, "compact", "csv", APIKEY)

# outputsize in ["compact", "full"]

### Do the API call to AlphaVantage
r = requests.get(call)
rlist = r.text.rstrip().split("\r\n")[1:]
m = len(rlist)
for line in reversed(rlist):
    print(str(tuple([SYMBOL] + line.split(","))))

sys.stdout.flush()
