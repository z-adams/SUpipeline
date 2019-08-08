import ctypes
from subprocess import Popen, PIPE
from threading import Thread
import numpy as np
import struct
import os

X_PATH = "{0}{1}".format(os.path.dirname(os.path.abspath(__file__)), "/pymarch.x")
#libmarch = ctypes.cdll.LoadLibrary("./libmarch.so")

#class CLOUD(ctypes.Structure):
#    _fields_ = [('x', ctypes.c_float),
#                ('y', ctypes.c_float),
#                ('z', ctypes.c_float),
#                ('r', ctypes.c_float),
#                ('density', ctypes.c_float)]

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

    #data = (CLOUD*n_clouds)()

    args = [X_PATH, "{0:d}".format(n_clouds), "{0:f}".format(resolution)]

    proc = Popen(args, stdin=PIPE, stdout=PIPE)

    #with open("binary_clouds.hx", 'wb+') as f:

    for i, vol in enumerate(volumes):
        proc.stdin.write(struct.pack(cloud_fmt,
            vol.x, vol.y, vol.z, vol.r, 1))
        #f.write(struct.pack(cloud_fmt, vol.x, vol.y, vol.z, vol.r, 1))

    #with open("stdout.txt", "wb+", 0) as f:
    #    while True:
    #        dat = proc.stdout.read(1)
    #        f.write(dat)

    data_u = bin_to_int(proc.stdout.read(4))
    data_v = bin_to_int(proc.stdout.read(4))
    print("U,V: {}, {}".format(data_u, data_v))
    data = np.zeros((data_u, data_v,))
    for i in range(data_u):
        for j in range(data_v):
            data[i, j] = bin_to_float(proc.stdout.read(4))

    return data
        #proc.stdout.read()
        #data[i] = CLOUD(vol.x, vol.y, vol.z, vol.r, vol.density)
    #libmarch.load(n_clouds, data, resolution, projection)  # load cloud data
    #start()  # begin raymarching
  
