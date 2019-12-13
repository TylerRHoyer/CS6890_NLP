import numpy as np
from matplotlib import pyplot as plt
from math import sqrt, ceil
import pickle
from multiprocessing import Pool
from datetime import datetime

# These should be set to topics with highest coherence.
keep = [5, 6, 7, 12, 19, 23, 29]

def load(filename):
	return np.array(pickle.load(open(filename, 'rb')))

# X = load('times.pck')
# data = load('sentiments.pck')
# window_size = 400

# print(data.shape)

# contrib = np.zeros((data.shape[0], data.shape[2]))
# for i in range(0, data.shape[0]):
# 	for t in range(0, data.shape[2]):
# 		contrib[i, t] = data[i, 2, t] - data[i, 0, t]

# ind = np.zeros((data.shape[0], data.shape[2], window_size), np.int)
# for t in range(0, data.shape[2]):
# 	n = 0
# 	ind_t = -np.ones(window_size, np.int)
# 	for i in range(1, data.shape[0]):
# 		cont = contrib[i, t]
# 		if cont >= 1e-9 or cont <= -1e-9:
# 			if n == window_size:
# 				for j in range(1, window_size):
# 					ind_t[j-1] = ind_t[j]
# 				ind_t[window_size - 1] = i
# 			else:
# 				ind_t[n] = i
# 				n += 1
# 		ind[i, t, :] = ind_t

# print('windowed avg and std...')
# def accum(i):
# 	acc = np.zeros(data.shape[2])
# 	std = np.zeros(data.shape[2])
# 	for t in range(0, data.shape[2]):
# 		n = 0
# 		for j in ind[i, t]:
# 			if j == -1:
# 				break
# 			n = n + 1
# 			acc[t] += contrib[j, t]
# 		if n == 0:
# 			acc[t] = 0
# 			std[t] = 0
# 			continue
# 		acc[t] /= n
# 		for j in range(window_size):
# 			if i - j < 0:
# 				break
# 			std[t] += (contrib[i-j, t] - acc[t])**2
# 		if n == 1:
# 			std[t] = 0
# 		else:
# 			std[t] = sqrt(std[t] / (window_size - 1))
# 	return acc, std

# results = Pool(32).map(accum, range(data.shape[0]))

# acc = np.zeros((data.shape[0], data.shape[2]))
# std = np.zeros((data.shape[0], data.shape[2]))
# i = 0
# for result in results:
# 	acc[i, :] = result[0]
# 	std[i, :] = result[1]
# 	i += 1

# print('Saving')

# pickle.dump(acc, open('avg.pck', 'wb'))
# pickle.dump(std, open('std.pck', 'wb'))
X = load('times.pck')
data = load('sentiments.pck')
acc = load('avg.pck')
std = load('std.pck')

print('Plotting')

length = 1000
sample = 20
start = -length*sample
X = X[start::sample].astype(np.int)
data = data[start::sample, :, :]
acc = acc[start::sample, :]
std = std[start::sample, :]

num_topics = len(keep)#data.shape[2]
x = ceil(sqrt(num_topics))
y = ceil(num_topics / x)
j = 1
for i in keep:#range(num_topics):
	print(i)
	j = j + 1
	print(acc[:, i])
	plt.plot(X, acc[:, i], label=f'Topic {i}')
	# plt.plot(X, acc[:, i] + std[:, i], label='Upper Sigma')
	# plt.plot(X, acc[:, i] - std[:, i], label='Lower Sigma')
	# plt.legend(loc='lower left')
plt.xlabel('UTC timestamp')
plt.ylabel('Sentiment')
plt.legend()
plt.title('Sentiments of 7 topics over time')

print(int(X[0]))
print(int(X[-1]))
tick_x = np.linspace(int(X[0]), int(X[-1]), 10)
tick_l = []
for x in tick_x:
	print(x)
	# Original timestamp was in milliseconds,
	# This datetime assumes seconds
	tick_l.append(datetime.fromtimestamp(x/1000).strftime("%m/%d/%y"))
plt.xticks(tick_x, tick_l)

# Add legend
plt.show()

n = len(keep)
c = 1
for i in [keep[3]]:#keep:
	for j in [keep[5]]:#keep:
		#plt.subplot(n, n, c)
		plt.plot(acc[:, i], acc[:, j])
		plt.xlabel(f'Sentiment of Topic {i}')
		plt.ylabel(f'Sentiment of Topic {j}')
		c += 1
plt.title('Relationship of two sentiments over time')
plt.show()