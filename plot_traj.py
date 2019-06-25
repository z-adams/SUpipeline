from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import re

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

first = True

x = []
y = []
z = []

with open("traj_path") as f:
    split = []
    for line in f:
        if line[0] != '(':
            continue

        line = re.sub(r"[(:]", "", line)
        split = re.split(r"[,) ]", line)
        split = [float(i) for i in split[:3]]
        color = 'r' if first else 'b'
        ax.scatter(split[0], split[1], split[2], c=color, marker='o')
        x.append(split[0])
        y.append(split[1])
        z.append(split[2])
        first = False

ax.plot(x, y, z, zdir=z, c=color, alpha=0.4)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

plt.show()
