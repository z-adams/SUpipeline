# Processes a set of trajectories associated with a single primary electron
from math import floor
import numpy as np
import sys


# Global coordinate bounds, to be minimized in find_data_ranges()
min_x = 1  # cm, TODO initial placeholder until I know what it should be
min_y = 1
min_z = 1

# Scans data and trims simulation region accordingly
# Also eliminates the initial event representing the particle beam emission
# (since it's a huge outlier and irrelevant to charge generation)
def find_data_ranges(trajectories):
    global min_x
    global min_y
    global min_z
    CUTOFF = 1  # value past which we can exclude a datapoint from the set
    for traj in trajectories:
        for index, event in enumerate(traj.events):
            # Remove incident event so it doesn't cause problems later:
            if any(i > CUTOFF for i in [event["x"], event["y"], event["z"]]):
                print >> sys.stderr, "Delete evt #{} in traj {}: " \
                "{}".format(index, traj.traj, event)
                del traj.events[index]
                continue
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
# This doesn't seem to work properly
def adjust_volume(traj):
    global min_x
    global min_y
    global min_z
    # adjust boundaries and unit scale with new known minima
    for event in traj.events:
        event["x"] *= 1e4
        event["y"] *= 1e4
        event["z"] *= 1e4
        event["x"] -= min_x
        event["y"] -= min_y
        event["z"] -= min_z

        # Offset coordinates to center in simulation region (0-150 um)
        # TODO: These don't seem to be used in reference
        #event["x"] += 30
        #event["y"] += 5
        #event["z"] += 55

def process_impact(trajectories, max_length, N_grid):
    # Set up grid
    x = np.linspace(0, max_length, N_grid)
    y = np.linspace(0, max_length, N_grid)
    z = np.linspace(0, max_length, N_grid)

    voxel_length = float(max_length)/N_grid  # ~3um right now

    # Energy lost in each grid (primary output)
    E_lost = np.zeros((N_grid, N_grid, N_grid))

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
                print >> sys.stderr, \
                "index OoB: ({},{},{})".format(x_ind,y_ind,z_ind)
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
    #TODO: universal max_length and N_grid, yet individual volume dimensions?
    voxel_volume = (voxel_length*1e-6)**3
    # e- generation time, here 1 ps (in seconds)
    gen_time = 1e-12
    G = E_lost / eh_gen / voxel_volume / gen_time

    x *= 1e-6
    y *= 1e-6
    z *= 1e-6

    return x, y, z, G  # This is going to be very expensive, maybe pass as args
    #write_charge_gen_mat(x, y, z, G)

