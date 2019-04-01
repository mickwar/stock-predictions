import os
import time
import mysql.connector
import requests
import datetime

### Get credentials
with open(os.path.expanduser("~/.secrets/creds")) as f:
    username, password, apikey = f.read().split("\n")[:3]


### Create the database and table
mydb = mysql.connector.connect(
    host = "localhost",
    user = username,
    passwd = password
    )

mycursor = mydb.cursor()

# Check if finance database exists before creating
mycursor.execute("show databases")
r = mycursor.fetchall()
try:
    r.index(('finance',))
except:
    print("Creating the 'finance' database")
    mycursor.execute("create database finance")

# Check if stocks table exists before creating
mycursor.execute("use finance")
mycursor.execute("show tables")
r = mycursor.fetchall()
try:
    r.index(('stocks',))
except:
    print("Creating the 'stocks' table")
    mycursor.execute("create table stocks ( \
        symbol varchar(8), \
        marketdate date, \
        open decimal(18,4), \
        high decimal(18,4), \
        low decimal(18,4), \
        close decimal(18,4), \
        adjusted_close decimal(18,4), \
        volume int unsigned, \
        dividend_amount decimal(18,4), \
        split_coefficient decimal(9,4))")


### Do the initial API calls for the stocks and add to database
symbols = []
with open("stock_list") as f:
    for line in f.read().rstrip().split("\n"):
        symbols.append(line.split(" ")[0])

# Get last market date for each symbol
mycursor.execute("select symbol, max(marketdate) from stocks group by symbol")
r = mycursor.fetchall()

lastdates = [[]] * len(symbols)
for l in r:
    lastdates[symbols.index(l[0])] = l[1]

# Derive the query
endpoint = "https://www.alphavantage.co/query"
params = "&".join(("function={}", "symbol={}", "outputsize={}", "datatype={}", "apikey={}"))

for i in range(len(symbols)):
    print("Symbol: {}".format(symbols[i]))
    try:
        # Number of days since last update
        # We should still make sure we run the API call after the market has closed
        diff = (datetime.date.today() - lastdates[symbols.index(symbols[i])]).days
        if diff == 0:
            print("    - No new data to gather")
            continue
        if diff < 100:
            outputsize = "compact"
        else:
            outputsize = "full"
    except:
        # Exception occurs if an item in `symbols` isn't found in `sql_symbs`
        outputsize = "full"
    call = endpoint + "?" + params.format("TIME_SERIES_DAILY_ADJUSTED",
        symbols[i], outputsize, "csv", apikey)
    print("    " + "- Doing API call")
    r = requests.get(call)
    print("    " + "- Sending to database")
    for line in reversed(r.text.rstrip().split("\r\n")[1:]):
        mycursor.execute("insert into stocks values" + str(tuple([symbols[i]] + line.split(","))))
    # Alphavantage doesn't want us doing too many calls too close in time
    time.sleep(15)

mydb.commit()

