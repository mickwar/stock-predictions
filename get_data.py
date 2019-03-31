import os
import time
import mysql.connector
import requests

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
mycursor.execute("create database finance")
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

mydb.close()


### Do the initial API calls for the stocks and add to database
symbols = []
with open("stock_list") as f:
    for line in f.read().rstrip().split("\n"):
        symbols.append(line.split(" ")[0])

mydb = mysql.connector.connect(
    host = "localhost",
    user = username,
    passwd = password,
    database = "finance")
mycursor = mydb.cursor()

endpoint = "https://www.alphavantage.co/query"
params = "&".join(("function={}", "symbol={}", "outputsize={}", "datatype={}", "apikey={}"))

for i in range(len(symbols)):
    print("Symbol: {}".format(symbols[i]))
    call = endpoint + "?" + params.format("TIME_SERIES_DAILY_ADJUSTED",
        symbols[i], "full", "csv", apikey)
    print("    " + "- Doing API call")
    r = requests.get(call)
    print("    " + "- Sending to database")
    for line in reversed(r.text.rstrip().split("\r\n")[1:]):
        mycursor.execute("insert into stocks values" + str(tuple([symbols[i]] + line.split(","))))
    # Alphavantage doesn't want us doing too many calls too close in time
    time.sleep(15)

mydb.commit()

