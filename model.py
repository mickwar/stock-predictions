import os
import sys
import numpy as np
import requests
from datetime import date
from sklearn.linear_model import LinearRegression

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

# Should probably having some error checking here

# Feature names
# 0 date
# 1 open
# 2 high
# 3 low
# 4 close
# 5 adjusted close
# 6 volume
# 7 dividend amount
# 8 split coefficient

# Format response into numpy object
rlist = r.text.rstrip().split("\r\n")[1:]
m = len(rlist)
k = 9 # Known number of columns

x = np.zeros((m, k))
for i in range(m):
    line = rlist[i].split(",")
    d = line[0]
    # Convert date to number of days since 1 Jan 2000
    x[i, 0] = (date(int(d[0:4]), int(d[5:7]), int(d[8:10])) - date(2000, 1, 1)).days
    # Convert remaining values to floats
    x[i, 1:] = line[1:]

# Reverse order so the earlier days are at the top
x = np.flip(x, 0)

# Get response (adjusted close)
y = x[:,5]

# Get data for prediction (should be today's date)
predx = x[-1, :]

# Offset by one day
# The prediction is tomorrow's close
y = y[1:]
x = x[:-1, :]


### Scale the features to [0, 1], remove any singularites
xmin = np.min(x, 0)
xmax = np.max(x, 0)
ymin = np.min(y, 0)
ymax = np.max(y, 0)

tmpind = xmax - xmin != 0
x = x[:, tmpind]
predx = predx[tmpind]
xmin = xmin[tmpind]
xmax = xmax[tmpind]

x = (x - xmin) / (xmax - xmin)
predx = (predx - xmin) / (xmax - xmin)
y = (y - ymin) / (ymax - ymin)


### Train a model
reg = LinearRegression().fit(x, y)
predy = reg.predict(predx.reshape(1, -1))

# Prediction error
stdev = np.sqrt(sum((reg.predict(x) - y)**2) / (len(y) - 2))

# Prediction interval
predyint = np.array([predy - 1.96 * stdev, predy, predy + 1.96 * stdev])
predyint = predyint * (ymax - ymin) + ymin


# Output back for node to pick up
for p in predyint:
    print(float(p))

sys.stdout.flush()
