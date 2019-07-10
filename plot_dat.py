from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from traj_parser import *

DATA_FRAC = 5 # graph every nth data point
LINE_ONLY = True # plot only lines (not points) for trajectories
SCALE = 1e4 # scale the units
ASSUME_FILENAME = True # assume dat file is called 'pe-trajectories.dat'
DEFAULT_FILE = 'pe-trajectories.dat'

def plot_dat(trajectories=None, filename=None):
    """ Plot a set of particle trajectories from pyPENELOPE
    If a list of parsed trajectories or the filename of a .dat file to parse
    is not specified, will prompt for a data filepath
    
    args:
    trajectories -- a list of trajectories to plot
    filename -- path to a .dat file to parse
    
    returns nothing
    """
    if trajectories is None:
        if filename is None:
            if ASSUME_FILENAME:
                if os.path.isfile(DEFAULT_FILE):
                    filename = DEFAULT_FILE
        if filename is None:
            print "current location: {}".format(os.getcwd())
            filename = raw_input("Where is the .dat file?: ")
        trajectories = parse_traj(filename, trim=True)

    first = True

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    tracks = []

    for traj in trajectories:
        tracks.append([[], [], []])
        for index, event in enumerate(traj.events):
            event['x'] *= SCALE
            event['y'] *= SCALE
            event['z'] *= SCALE
            color = 'r' if first else 'b'
            if (index % 10 == 0 and not LINE_ONLY) or (first and LINE_ONLY):
                ax.scatter(event['x'], event['y'], event['z'],
                        c=color, marker='o')
            tracks[-1][0].append(event['x'])
            tracks[-1][1].append(event['y'])
            tracks[-1][2].append(event['z'])
            first = False
            
    for track in tracks:
        ax.plot(track[0], track[1], track[2], zdir=track[2], c=color, alpha=0.4)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.show()

if __name__ == '__main__':
    plot_dat()
