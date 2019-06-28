# Processes a set of trajectories associated with a single primary electron
import numpy as np
import sys
from math import ceil


# Global coordinate bounds, to be minimized in find_data_ranges()
min_x = 1e10  # um, TODO initial placeholder until I know what it should be
min_y = 1e10
min_z = 1e10
max_x = -1e10
max_y = -1e10
max_z = -1e10

minima = [1e10, 1e10, 1e10]
maxima = [-1e10, -1e10, -1e10]
coords = ['x', 'y', 'z']

## Scans data to find its boundaries, converts from cm to um,
## translates it such that all coordinates are positive
def preprocess_data(trajectories):
    global minima
    global maxima
    global coords
    for traj in trajectories:
        for index, event in enumerate(traj.events):
            # convert cm to um
            for e in coords:
                event[e] *= 1e4

            # search for minimized coordinates
            for i, e in enumerate(coords):
                if minima[i] > event[e]:
                    minima[i] = event[e]

    # Translate data to have all positive coordinates
    for traj in trajectories:
        for event in traj.events:
            for i, e in enumerate(coords):
                event[e] -= minima[i] 

    minima = [1e10, 1e10, 1e10]
    # Calculate maxima
    for traj in trajectories:
        for index, event in enumerate(traj.events):
            for i, e in enumerate(coords):
                if maxima[i] < event[e]:
                    maxima[i] = ceil(event[e])
                # debug: recalculate minimum
                if minima[i] > event[e]:
                    minima[i] = event[e]
    pass

def process_impact(trajectories, N_grid):
    # Set up grid

    # Energy lost in each grid (primary output)
    E_lost = np.zeros((N_grid, N_grid, N_grid))

    preprocess_data(trajectories)

    x = np.linspace(0, maxima[0], N_grid)
    y = np.linspace(0, maxima[1], N_grid)
    z = np.linspace(0, maxima[2], N_grid)

    x_grid_spacing = float(maxima[0])/N_grid
    y_grid_spacing = float(maxima[1])/N_grid
    z_grid_spacing = float(maxima[2])/N_grid

    # compute energy deposition distribution over voxels
    for traj in trajectories:

        x_traj = np.array([evt['x'] for evt in traj.events])
        y_traj = np.array([evt['y'] for evt in traj.events])
        z_traj = np.array([evt['z'] for evt in traj.events])
        

        E_left = [e["E"] for e in traj.events]
        
        E_prev = E_left[0] #traj.events[0]["E"]

        # Assign energy lost to each grid element
        #for index, event in enumerate(traj.events):
        for i in range(len(traj.events)):
            #x_ind = int(event["x"] / voxel_length)
            #y_ind = int(event["y"] / voxel_length)
            #z_ind = int(event["z"] / voxel_length)
            x_ind = np.argmin(np.abs(x - x_traj[i]))
            y_ind = np.argmin(np.abs(y - y_traj[i]))
            z_ind = np.argmin(np.abs(z - z_traj[i]))
            #E_lost[x_ind, y_ind, z_ind] += abs
        
            #delta_E = E_prev - event["E"]
            delta_E = E_prev - E_left[i]
            if delta_E > 0:
                #print "({},{},{}):\t{}".format(x_ind, y_ind, z_ind, delta_E)
                #print "({},{},{}):\t{}".format(event["x"], event["y"], event["z"], delta_E)
                # I think it's ok for these to be here...
                E_lost[x_ind, y_ind, z_ind] += delta_E
                #E_prev = event["E"]
                E_prev = E_left[i]


    # compute energy generation rate from energy lost
    # Generation rate has a unit of m^-3 * s^-1
    # electron-hole pair production energy for CdTe: 4.43 eV
    eh_gen = 4.43  # for CdTe
    voxel_volume = x_grid_spacing*y_grid_spacing*z_grid_spacing*1e-18  #(1e6)^3
    # e- generation time, here 1 ps (in seconds)
    gen_time = 1e-12
    G = E_lost / eh_gen / voxel_volume / gen_time

    # convert back to meters
    x *= 1e-6
    y *= 1e-6
    z *= 1e-6

    return x, y, z, G  # This is going to be very expensive, maybe pass as args
    #write_charge_gen_mat(x, y, z, G)

