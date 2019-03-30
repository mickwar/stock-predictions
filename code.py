import mysql.connector

#mydb = mysql.connector.connect(
#    host="localhost",
#    user="",
#    passwd=""
#    )
#
#mycursor = mydb.cursor()
#mycursor.execute("create database finance")
#mycursor.execute("create table stocks ( \
#    symbol varchar(8), \
#    marketdate date, \
#    open decimal(18,4), \
#    high decimal(18,4), \
#    low decimal(18,4), \
#    close decimal(18,4), \
#    volume int unsigned, \
#    dividend_amount decimal(18,4), \
#    split_coefficient decimal(9,4))")


mydb = mysql.connector.connect(
    host = "localhost",
    user = "",
    passwd = "",
    database = "finance")

mycursor = mydb.cursor()

mycursor.execute("show tables")
for x in mycursor:
    print(x)


mycursor.execute("select * from stocks")
for x in mycursor:
    print(x)


