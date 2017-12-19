import numpy as np
import matplotlib.pyplot as plt

x = np.random.random([5,5])
#print(x)
b=0.89
y = (1-b)*x+b
delta = []

for i in range(100):
    b = i/100
    y_hat = (1-b)*x+b
    #print(y_hat)
    temp = np.dot(np.array(y-y_hat).reshape([1,-1]),np.array(y-y_hat).reshape([-1,1]))/25
    delta.append(temp[0])

plt.plot(delta)
plt.show()
