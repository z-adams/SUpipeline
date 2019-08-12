import ctypes
from subprocess import Popen, PIPE
from threading import Thread
import numpy as np
import time
import struct
import os

X_PATH = "{0}{1}".format(os.path.dirname(os.path.abspath(__file__)), "/pymarch.x")

class Cloud:
    def __init__(self, x, y, z, r, d):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        self.d = d

def bin_to_int(string):
    i = struct.unpack("@i", string)
    return i[0]

def bin_to_float(string):
    f = struct.unpack("@f", string)
    return f[0]

def run_raymarcher(volumes, resolution, projection):

    cloud_fmt = "@fffff"

    n_clouds = len(volumes)

    args = [X_PATH, "{0:d}".format(n_clouds), "{0:f}".format(resolution)]

    proc = Popen(args, stdin=PIPE, stdout=PIPE)

    for i, vol in enumerate(volumes):
        proc.stdin.write(struct.pack(cloud_fmt,
            vol.x, vol.y, vol.z, vol.r, vol.density()))

    # Finished data transfer, begin run
    start = time.time()

    data_u = bin_to_int(proc.stdout.read(4))
    data_v = bin_to_int(proc.stdout.read(4))

    # Data from proc -> simulation complete
    elapsed = time.time() - start

    print("Simulation completed in {0:.4f} seconds".format(elapsed))
    print("Recieved data dimensions (U,V): {}, {}".format(data_u, data_v))
    data = np.zeros((data_u, data_v,))
    for i in range(data_u):
        for j in range(data_v):
            data[i, j] = bin_to_float(proc.stdout.read(4))

    return data
  
