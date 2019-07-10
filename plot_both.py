from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from traj_parser import *
import scipy.io as sio

DATA_FRAC = 5 # graph every nth data point
LINE_ONLY = True # graph only lines (not points) for raw events
DAT_SCALE = 1 # scale the datasets to match units
MAT_SCALE = 1e6

def plot_both(trajectories=None, dat=None, mat=None):
    """ Plots both a raw trajectory and charge generation data
    Since the .dat file usually contains extra information, typically
    this function is used with the dat kwarg excluded, comparing only
    a .mat charge data matrix and a parsed list of trajectories
    associated with the same shower as the .mat.

    args:
    trajectories -- the list of trajectories to plot
    dat -- plot a dat file's trajectories
    mat -- plot a mat file's trajectories

    returns nothing
    """
    if trajectories is None:
        if dat is None:
            print "current location: {}".format(os.getcwd())
            dat = raw_input("Where is the .dat file?: ")
        trajectories = parse_traj(dat, trim=True)
    if mat is None:
        mat = raw_input("Where is the .mat file?: ")
    mat = sio.loadmat(mat)

    first = True

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    tracks = []

    for traj in trajectories:
        tracks.append([[], [], []])
        for index, event in enumerate(traj.events):
            color = 'r' if first else 'b'
            if (index % 10 == 0 and not LINE_ONLY) or (first and LINE_ONLY):
                ax.scatter(event['x']*DAT_SCALE, event['y']*DAT_SCALE, 
                        event['z']*DAT_SCALE, c=color, marker='o')
            tracks[-1][0].append(event['x']*DAT_SCALE)
            tracks[-1][1].append(event['y']*DAT_SCALE)
            tracks[-1][2].append(event['z']*DAT_SCALE)
            first = False
            
    for track in tracks:
        ax.plot(track[0], track[1], track[2], zdir=track[2], c=color, alpha=0.4)

    x_bins = mat['x'].shape[1]
    y_bins = mat['y'].shape[1]
    z_bins = mat['z'].shape[1]

    for i in range(x_bins):
        for j in range(y_bins):
            for k in range(z_bins):
                if mat['G'][i][j][k] > 0:
                    color = 'r' if first else 'b'
                    first = False
                    ax.scatter(mat['x'][0][i]*MAT_SCALE, 
                            mat['y'][0][j]*MAT_SCALE, 
                            mat['z'][0][k]*MAT_SCALE,
                            c=color, marker='.')

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.show()

if __name__ == '__main__':
    plot_both()
