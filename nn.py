import tflearn
from tflearn import DNN
import numpy as np
import pickle
from matplotlib import pyplot as plt
from datetime import datetime

keep = [5, 6, 7, 12, 19, 23, 29]
n_topics = len(keep)

def load(filename):
	return np.array(pickle.load(open(filename, 'rb')))

# Load in data
t = load('times.pck').astype(np.int)
acc = load('avg.pck')
dAcc = np.zeros(acc.shape)

net = tflearn.input_data(shape=[None, 2, n_topics])
net = tflearn.fully_connected(net, 100)
net = tflearn.fully_connected(net, 20, activation='relu')
net = tflearn.fully_connected(net, 1)
net = tflearn.regression(net,
	optimizer='adam',
	loss='mean_square',
	metric='R2',
	learning_rate=0.01)
model = DNN(net)

# compute rates of change up to point
for i in range(1, acc.shape[0]):
	dAcc[i, :] = acc[i, :] - acc[i - 1, :]

# Convert to time steps by interpolation
min_t = t.min() # Jan 1st, 2019. Older data has too many gaps
max_t = t.max()
x = np.linspace(min_t, max_t, 1000).astype(np.int)

print(len(x))
print(x[1] - x[0])

# Make sure we are in the correct order
print(np.all(np.diff(t) >= 0))

# Interpolate the values to equal time spaces
i_acc = np.zeros((len(x), acc.shape[1]))
i_dAcc = np.zeros((len(x), acc.shape[1]))
for i in range(1, acc.shape[1]):
	i_acc[:, i] = np.interp(x, t, acc[:, i])
	i_dAcc[:, i] = np.interp(x, t, dAcc[:, i])
acc = i_acc
dAcc = i_dAcc

for topic in keep:
	plt.plot(x, acc[:, topic])
plt.show()

trg = keep[2]
X = np.zeros((acc.shape[0], 2, n_topics))
Y = np.zeros((acc.shape[0], 1))
for i in range(acc.shape[0] - 1):
	X[i, 0, :] = acc[i, keep]
	X[i, 1, :] = dAcc[i, keep]
	Y[i] = acc[i + 1, trg]

model.fit(X, Y.reshape(-1, 1), n_epoch=5, batch_size=15, shuffle=True)
Yhat = model.predict(X)

accuracy = Yhat - Y
a_m = accuracy.mean()
a_s = accuracy.std()
y_m = Y.mean()

print(f'Difference Mean = {np.abs(a_m) / y_m * 100}%')
print(f'Standard Deviation = {a_s / y_m * 100}%')

plt.scatter(Y, Yhat, s=1)
plt.title('Predicted Sentiment vs Actual Sentiment')
plt.ylabel('Predicted Sentiment')
plt.xlabel('Actual Sentiment')
plt.show()
print(model)