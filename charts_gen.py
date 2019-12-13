import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
from math import cos, sin, pi, sqrt, ceil
import pickle
from scipy.interpolate import interp1d

X = [2016, 2017, 2018, 2019, 2020, 2021]
Y = [
	[0.6, 0.7, 1.0, 1.0, 0.9, 0.7],
	[1, 0.5, 0.1, 0.2, 0.3, 0.5],
	[0.7, 0.6, 0.5, 0.6, 0.5, 0.6],
]

xnew_1 = np.linspace(2016, 2019, 16)
xnew_2 = np.linspace(2019, 2021, 8)

colors = ['red', 'green', 'blue']

for i in range(len(Y)):
	f = interp1d(X, Y[i], 'quadratic')
	plt.plot(xnew_1, f(xnew_1), label=f'Topic {i}', linestyle='-', color=colors[i])
	plt.plot(xnew_2, f(xnew_2), label=f'Predicted Topic {i}', linestyle=':', color=colors[i])
plt.legend(loc='lower left')
plt.xlabel('Year')
plt.ylabel('Relative Sentiment')
plt.title('Predicting Sentiment Example')
plt.show()