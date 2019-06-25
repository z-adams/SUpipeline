from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import scipy.io as sio

print "current location: {}".format(os.getcwd())
filename = raw_input("Where is the data file?: ")
mat = sio.loadmat(filename)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

first = True

x = []
y = []
z = []

#line = re.sub(r"[(:]", "", line)
#split = re.split(r"[,) ]", line)
#split = [float(i) for i in split[:3]]
#ax.scatter(split[0], split[1], split[2], c=color, marker='o')
#x.append(split[0])
#y.append(split[1])
#z.append(split[2])

for i in range(50):
    for j in range(50):
        for k in range(50):
            if mat['G'][i][j][k] > 0:
                color = 'r' if first else 'b'
                first = False
                ax.scatter(i, j, k, c=color, marker='o')
                x.append(i)
                y.append(j)
                z.append(k)

ax.plot(x, y, z, zdir=z, c=color, alpha=0.4)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

plt.show()
