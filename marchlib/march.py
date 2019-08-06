#from ctypes import cdll
import ctypes
from subprocess import Popen, PIPE
from threading import Thread
import struct

libmarch = ctypes.cdll.LoadLibrary("./libmarch.so")

class CLOUD(ctypes.Structure):
    _fields_ = [('x', ctypes.c_float),
                ('y', ctypes.c_float),
                ('z', ctypes.c_float),
                ('r', ctypes.c_float),
                ('density', ctypes.c_float)]

def run_raymarcher(volumes, resolution, projection):

    initmarch()  # initialize libmarch

    n_clouds = len(volumes)

    data = (CLOUD*n_clouds)()

    #load_thread = Thread(target=libmarch.load,
    #        args=(n_clouds, resolution, projection,))
    #load_thread.start()  #

    for i, vol in enumerate(volumes):
        data[i] = CLOUD(vol.x, vol.y, vol.z, vol.r, vol.density)
        
    libmarch.load(n_clouds, data, resolution, projection)  # load cloud data
    start()  # begin raymarching
    
