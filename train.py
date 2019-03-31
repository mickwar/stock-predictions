import os
import time
import mysql.connector
import requests
import datetime

### Get credentials
with open(os.path.expanduser("~/.secrets/creds")) as f:
    username, password, _ = f.read().split("\n")[:3]

###
mydb = mysql.connector.connect(
    host = "localhost",
    user = username,
    passwd = password,
    database = "finance")

# A better way for getting Decimal class
class myconverter(mysql.connector.conversion.MySQLConverter):
    def _NEWDECIMAL_to_python(self, value, desc=None):
        return float(value)

mydb.set_converter_class(myconverter)
mycursor = mydb.cursor()

mycursor.execute("select * from stocks limit 10;")
myresult = mycursor.fetchall()
for x in myresult:
    print(x)


