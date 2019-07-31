from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import scipy.io as sio

def plot_traj(filename=None):
    """ Plot volume charge data from a .mat file
    Will prompt for a data filepath if none is specified

    args:
    filename -- the data filepath
    """
    if filename is None:
        print "current location: {}".format(os.getcwd())
        filename = raw_input("Where is the data file?: ")
    mat = sio.loadmat(filename)
    G = mat['G']

    fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax = fig.gca(projection='3d')

    x = []
    y = []
    z = []

    x_bins = mat['x'].shape[1]
    y_bins = mat['y'].shape[1]
    z_bins = mat['z'].shape[1]

    colors = np.where(mat['G'] > 0., '#FF0000', '#000000')
    #filled = np.zeros(mat['G'].shape, dtype=bool)
    filled = np.where(G > 0., 1, 0)
    

    first = True
    for i in range(x_bins):
        for j in range(y_bins):
            for k in range(z_bins):
                if mat['G'][i][j][k] > 0:
                    color = 'r' if first else 'b'
                    first = False
                    #ax.scatter(i, j, k, c=color, marker='o')
                    x.append(i)
                    y.append(j)
                    z.append(k)

    #ax.plot(x, y, z, zdir=z, c=color, alpha=0.4)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.voxels(filled, facecolors=colors)

    plt.show()

if __name__ == '__main__':
    plot_traj()
