import os
import mysql.connector
import datetime
import numpy as np
import pandas as pd

### Get credentials
with open(os.path.expanduser("~/.secrets/creds")) as f:
    username, password, _ = f.read().split("\n")[:3]

### Connect to database
mydb = mysql.connector.connect(
    host = "localhost",
    user = username,
    passwd = password,
    database = "finance")

### Get training data
x = pd.read_sql("select * from stocks;", con = mydb)

