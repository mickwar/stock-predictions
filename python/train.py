import os
import mysql.connector
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from keras.models import Model
from keras.layers import Input, Dense, GRU, Dropout, BatchNormalization
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
rawdat = pd.read_sql("select * from stocks where symbol = 'MMM';", con = mydb)

def create_dataset(dat, look_back, M):
    tmp = dat.copy()
    tmp.marketdate = (tmp.marketdate - datetime.date(2000, 1, 1)).dt.days
    tmp = tmp.drop('symbol', 1)
    # log returns
    y = np.log(tmp.shift(-1).tail(len(tmp) - look_back).adjusted_close / tmp.tail(len(tmp) - look_back).adjusted_close)
    # some transforms
    tmp.volume = np.log(tmp.volume)
    tmp -= tmp.min()
    tmp /= tmp.max()
    x = np.zeros((tmp.shape[0] - look_back, look_back, tmp.shape[1]))
    for i in range(look_back):
        x[:, i, :] = tmp.shift(i).tail(len(tmp) - look_back)
    x = np.delete(x, len(x)-1, 0)
    y = y[:-1]
    trainx = x[:M, :, :]
    trainy = y[:M]
    testx = x
    testy = y
    return trainx, trainy, testx, testy


look_back = 50
trainx, trainy, testx, testy = create_dataset(rawdat, look_back, 5000)



plt.clf()
#plt.plot(trainx.marketdate, trainy)
plt.plot(trainx[:,0,0], trainy)
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

inputs = Input((look_back, trainx.shape[2]))
layer = GRU(32, return_sequences = True)(inputs)
layer = Dropout(0.2)(layer)
#layer = BatchNormalization()(layer)
#layer = GRU(64, return_sequences = True)(layer)
#layer = Dropout(0.2)(layer)
#layer = BatchNormalization()(layer)
layer = GRU(32)(layer)
layer = Dropout(0.2)(layer)
#layer = BatchNormalization()(layer)
outputs = Dense(len(q))(layer)
model = Model(inputs = inputs, outputs = outputs)
model.compile(loss = qloss, optimizer = "adadelta")
model.fit(x = trainx, y = trainy, epochs = 50, verbose = 1, batch_size = 64)

predy = model.predict(testx)

plt.clf()
plt.plot(testx[:,0,0], testy, color = (0,0,0))
plt.plot(testx[:,0,0], predy[:,0])
plt.plot(testx[:,0,0], predy[:,1])
plt.plot(testx[:,0,0], predy[:,2])
plt.show(block = False)

np.exp(predy).shape
rawdat.adjusted_close.shape

newy = rawdat.adjusted_close[50:-1, None] * np.exp(predy)

plt.clf()
plt.plot(rawdat.marketdate, rawdat.adjusted_close)
plt.plot(rawdat.marketdate[51:], newy[:,0])
plt.plot(rawdat.marketdate[51:], newy[:,1])
plt.plot(rawdat.marketdate[51:], newy[:,2])
plt.xlim((datetime.date(2019,1,1), datetime.date(2019,5,1)))
plt.ylim((170, 220))
plt.show(block = False)

plt.plot(testx[:,0,0], testy, color = (0,0,0))
plt.plot(testx[:,0,0], predy[:,0])
plt.plot(testx[:,0,0], predy[:,1])
plt.plot(testx[:,0,0], predy[:,2])
plt.show(block = False)



### Just a standard feedforward network
look_back = 1
trainx, trainy, testx, testy = create_dataset(rawdat, look_back, 5000)
trainx = np.squeeze(trainx)
trainy = np.squeeze(trainy)
testx = np.squeeze(testx)
testy = np.squeeze(testy)

def make_quantile(q):
    q = np.array(q)
    def loss(y_true, y_pred):
        e = y_true - y_pred
        return K.mean(K.maximum(q*e, (q-1)*e), axis = -1)
    return loss

q = [0.1, 0.5, 0.9]
qloss = make_quantile(q)

inputs = Input((trainx.shape[1],))
layer = Dense(32, activation = "relu")(inputs)
layer = Dropout(0.2)(layer)
layer = Dense(32, activation = "relu")(layer)
layer = Dropout(0.2)(layer)
outputs = Dense(len(q))(layer)
model = Model(inputs = inputs, outputs = outputs)
model.compile(loss = qloss, optimizer = "adadelta")
model.fit(x = trainx, y = trainy, epochs = 500, verbose = 1, batch_size = 64)

predy = model.predict(testx)

plt.clf()
plt.plot(testx[:,0], testy, color = (0,0,0))
plt.plot(testx[:,0], predy[:,0])
plt.plot(testx[:,0], predy[:,1])
plt.plot(testx[:,0], predy[:,2])
plt.show(block = False)

newy = rawdat.adjusted_close[1:-1, None] * np.exp(predy)

plt.clf()
plt.plot(rawdat.marketdate, rawdat.adjusted_close, color = (0,0,0))
plt.plot(rawdat.marketdate[2:], newy[:,0])
plt.plot(rawdat.marketdate[2:], newy[:,1])
plt.plot(rawdat.marketdate[2:], newy[:,2])
plt.xlim((datetime.date(2018,1,1), datetime.date(2019,5,1)))
plt.show(block = False)

