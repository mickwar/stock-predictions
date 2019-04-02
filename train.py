import os
import mysql.connector
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from keras.models import Model
from keras.layers import Input, Dense
from keras import backend as K

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
dat = pd.read_sql("select * from stocks where symbol = 'MMM';", con = mydb)
x = dat.copy()

#x.loc[x.symbol == 'MMM']
#for d in x.loc[x.symbol == 'MMM'].marketdate:
#    print((d, d.year - 2000, (d.month - 1) // 3 + 1), d.weekday())

#plt.clf()
#plt.plot(x.marketdate, x.adjusted_close)
#plt.show(block = False)


# Response:
# Log of tomorrow's adjusted close divided by today's adjusted close
#y = np.log(x.shift(-1).adjusted_close / x.adjusted_close)
y = x.shift(-1).adjusted_close


# Worry about covariates later, just remove date for now
x.columns
x.marketdate = (x.marketdate - datetime.date(2000, 1, 1)).dt.days
#x = x.drop('marketdate', 1)
x = x.drop('symbol', 1)

# Scale the input
x -= x.min()
x /= x.max()

trainx = x.drop(x.tail(1).index)
trainy = y.drop(y.tail(1).index)


plt.clf()
plt.plot(trainx.marketdate, trainy)
plt.show(block = False)

# A simple quantile regression
def make_quantile(q):
    q = np.array(q)
    def loss(y_true, y_pred):
        e = y_true - y_pred
        return K.mean(K.maximum(q*e, (q-1)*e), axis = -1)
    return loss

q = [0.1, 0.5, 0.9]
qloss = make_quantile(q)

inputs = Input((trainx.shape[1],))
layer = Dense(32, activation = 'relu')(inputs)
layer = Dense(32, activation = 'relu')(layer)
layer = Dense(32, activation = 'relu')(layer)
outputs = Dense(len(q), activation = 'linear')(layer)
model = Model(inputs = inputs, outputs = outputs)
model.compile(loss = qloss, optimizer = 'adadelta')
model.fit(x = trainx, y = trainy, epochs = 5000, verbose = 1, batch_size = 64)

predy = np.squeeze(model.predict(trainx))

plt.clf()
_ = plt.plot(trainy)
_ = plt.plot(predy[:,0])
_ = plt.plot(predy[:,1])
_ = plt.plot(predy[:,2])
plt.show(block = False)

#plt.clf()
#plt.plot(trainy, predy[:,1])
#plt.show(block = False)
