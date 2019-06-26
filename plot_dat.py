from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import os
from parser import *

print "current location: {}".format(os.getcwd())
filename = raw_input("Where is the .dat file?: ")
trajectories = parse(filename, trim=True)

first = True

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

#tracks = []

for traj in trajectories:
    #tracks.append([[], [], []])
    for event in traj.events:
        color = 'r' if first else 'b'
        first = False
        ax.scatter(event['x'], event['y'], event['z'], c=color, marker='o')
        #tracks[-1][0].append(event['x'])
        #tracks[-1][1].append(event['y'])
        #tracks[-1][2].append(event['z'])
        
#for track in tracks:
#    ax.plot(track[0], track[1], track[2], zdir=track[2], c=color, alpha=0.4)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
plt.show()
