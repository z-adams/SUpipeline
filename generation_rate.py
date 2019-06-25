import scipy.io as sio
import numpy as np
from math import floor
import os
import sys
from collections import namedtuple

# Global coordinate bounds, to be minimized in find_data_ranges()
min_x = 1  # cm, TODO initial placeholder until I know what it should be
min_y = 1
min_z = 1

class Trajectory:
    def __init__(self, TRAJ, KPAR, PARENT, ICOL, EXIT):
        self.traj = TRAJ
        self.kpar = KPAR
        self.parent = PARENT
        self.icol = ICOL
        self.exit = EXIT
        self.events = []

def write_charge_gen_mat(x, y, z, G):
    # Matlab arrays are 2D "column vectors" with shape (1, m)
    # Here I transpose them to be 1 column of m (-1: automatic) elements
    np.reshape(x, (1, -1))
    np.reshape(y, (1, -1))
    np.reshape(z, (1, -1))
    data = {"x": x, "y": y, "z": z, "G": G}
    mat = raw_input("Where should I save the data?: ")
    sio.savemat(mat, data)
    #sio.savemat("../test.mat", data)

def find_data_ranges(trajectories):
    global min_x
    global min_y
    global min_z
    for traj in trajectories:
        for event in traj.events:
            # search for minimized coordinates
            if min_x > event["x"]:
                min_x = event["x"]
            if min_y > event["y"]:
                min_y = event["y"]
            if min_z > event["z"]:
                min_z = event["z"]
    min_x *= 1e4
    min_y *= 1e4
    min_z *= 1e4

# would be simplefied by using np probably but this is fine for now
def adjust_volume(traj):
    global min_x
    global min_y
    global min_z
    # TODO bug: huge outlier in x (traj1) (manually stripping in parse for now)
    # adjust boundaries and unit scale with new known minima
    for event in traj.events:
        event["x"] *= 1e4
        event["y"] *= 1e4
        event["z"] *= 1e4
        event["x"] -= min_x
        event["y"] -= min_y
        event["z"] -= min_z

        # TODO ??? find out what this does
        # Offset coordinates to center in simulation region (0-150 um)
        event["x"] += 30
        event["y"] += 5
        event["z"] += 55


################### PARSER ####################
# Assumptions: lines with comments will contain only comments
# Special considerations:
# first event contains the initial position and energy of the incident particle
# 
def parse(filename, trajectories):
    # read raw file into buffer
    buf = []
    with open(filename, 'r') as f:
        for line in f:
            # skip comments
            if line.find('#') != -1:
                continue
            buf.append(line)

    # parse by traj
    num_lines = len(buf)
    i = 0
    while i < num_lines:
        line = buf[i]

        # parse header, begin new trajectory
        if line[0] == '0':
            # file ends with line of 00000000s, exit if at end
            if i == num_lines - 1:
                break

            info = []
            # header length is hardcoded (5 elements)
            for j in range(5):
                i += 1
                # take the number at the end of each header line and continue
                info.append(int(buf[i].split()[1]))
            trajectories.append(
                    Trajectory(info[0], info[1], info[2], info[3], info[4]))
            i += 2 # skip over the '111111...' line to first line of data
            continue

        split_line = line.split()

        # append event to event list
        trajectories[-1].events.append({
            "x": float(split_line[0]),
            "y": float(split_line[1]),
            "z": float(split_line[2]),
            "E": float(split_line[3]),
            "WGHT": float(split_line[4]),
            "IBODY": int(split_line[5]),
            "ICOL": int(split_line[6])})
        #debug
        event = trajectories[-1].events[-1]
        print "({},{},{})".format(event["x"], event["y"], event["z"])
        i += 1

# tuple to store a single event from pyPENELOPE
#Event = namedtuple("Event", ["x", "y", "z", "E", "WGHT", "IBODY", "ICOL"])
# actually instead I'm just going to use dicts with the same members
#event = {"x": x, "y": y, "z": z, "E": E, "WGHT": W, "IBODY": B, "ICOL": C}

# Set up grid
max_length = 150  # max length of grid/grid boundary (um)
                  # must include all data points
N_grid = 51       # number of grid elements in each dimension

x = np.linspace(0, max_length, N_grid)
y = np.linspace(0, max_length, N_grid)
z = np.linspace(0, max_length, N_grid)

voxel_length = float(max_length)/N_grid  # ~3um right now

# Energy lost in each grid (primary output)
E_lost = np.zeros((N_grid, N_grid, N_grid))

# list of trajectories generated in pyPENELOPE
trajectories = []

print "location: {}".format(os.getcwd())
dat = raw_input("Where is the data?: ")
parse(dat, trajectories)
print "\n"
#parse("../test.dat", trajectories)

find_data_ranges(trajectories)
# compute energy deposition distribution over voxels
for traj in trajectories:

    adjust_volume(traj)

    E_prev = traj.events[0]["E"]

    # Assign energy lost to each grid element
    for event in traj.events:
        x_ind = int(floor(event["x"] / voxel_length))
        y_ind = int(floor(event["y"] / voxel_length))
        z_ind = int(floor(event["z"] / voxel_length))
        
        # TODO HACK: some are out of bounds
        if (x_ind > 50 or y_ind > 50 or z_ind > 50):
            print >> sys.stderr, "index OoB: ({},{},{})".format(x_ind,y_ind,z_ind)
            continue
    
        delta_E = E_prev - event["E"]
        if delta_E > 0:
            #print "({},{},{}):\t{}".format(x_ind, y_ind, z_ind, delta_E)
            #print "({},{},{}):\t{}".format(event["x"], event["y"], event["z"], delta_E)
            # I think it's ok for these to be here...
            E_lost[x_ind, y_ind, z_ind] += delta_E
            E_prev = event["E"]

# compute energy generation rate from energy lost
# Generation rate has a unit of m^-3 * s^-1
# electron-hole pair production energy for CdTe: 4.43 eV
eh_gen = 4.43
#TODO question: universal max_length and N_grid, yet individual volume dimensions?
voxel_volume = voxel_length**3
# e- generation time, here 1 ps (in seconds)
gen_time = 1e-12
G = E_lost / eh_gen / voxel_volume / gen_time

x *= 1e-6
y *= 1e-6
z *= 1e-6

write_charge_gen_mat(x, y, z, G)
print("done")
#### now what? How does Lumerical want this?

