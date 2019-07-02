# Processes a set of trajectories associated with a single primary electron
import numpy as np
import sys
from math import ceil, sqrt


# Global coordinate bounds, to be minimized in find_data_ranges()
minima = [1e10, 1e10, 1e10] # initial guesses, TODO change maybe
maxima = [-1e10, -1e10, -1e10]
coords = ['x', 'y', 'z']

## Scans data to find its boundaries, converts from cm to um,
## translates it such that all coordinates are positive
def preprocess_data(trajectories):
    """ Scans the parsed trajectories and finds the minimum and maximum limits
    of the data to later trim the simulation volume.

    args:
    trajectories -- the list of trajectories to be contained in the sim volume

    returns nothing - acts on globals
    """
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
                #if minima[i] > event[e]:
                #    minima[i] = event[e]

def deltaX(event0, event1):
    dxx = (event0['x'] - event1['x'])**2
    dyy = (event0['y'] - event1['y'])**2
    dzz = (event0['z'] - event1['z'])**2
    return sqrt(dxx + dyy + dzz)

def process_impact(trajectories, N_grid):
    """ Compute charge generation data from a shower of trajectories

    args:
    trajectories -- the list of trajectories representing the shower
    N_grid -- the grid resolution (number of divisions, all dimensions)

    returns x, y, z, G - lists containing the grid divisions (x,y,z), and
    charge volume data (G, x*y*z matrix)
    """

    # Energy lost in each grid (primary output)
    E_lost = np.zeros((N_grid, N_grid, N_grid))

    preprocess_data(trajectories)

    # Set up grid
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

        distance = 0

        # Assign energy lost to each grid element
        for i in range(len(traj.events)):
            x_ind = np.argmin(np.abs(x - x_traj[i]))
            y_ind = np.argmin(np.abs(y - y_traj[i]))
            z_ind = np.argmin(np.abs(z - z_traj[i]))
            #E_lost[x_ind, y_ind, z_ind] += abs
        
            #delta_E = E_prev - event["E"]
            delta_E = E_prev - E_left[i]
            if delta_E > 0:
                E_lost[x_ind, y_ind, z_ind] += delta_E
                #E_prev = event["E"]
                E_prev = E_left[i]

            #TODO hopefully this is ok (index shifted back by 1)
            if i == 0:
                dX = 0
            else:
                dX = deltaX(traj.events[i-1], traj.events[i])

            v = (sqrt((E_left[i]+511e3)**2 - 511e3**2)/(511e3+E_left[i]))*3e10
            if v == 0:
                t = 0
            else:
                t = dX / v

            distance += dX

    # Compute energy generation rate from energy lost (units: m^-3 * s^-1)

    eh_gen = 4.43 # electron-hole pair production energy for CdTe: 4.43 eV
    voxel_volume = x_grid_spacing*y_grid_spacing*z_grid_spacing*1e-18  #(1e6)^3

    # e- generation time, here 1 ps (in seconds)
    gen_time = 1e-12

    G = E_lost / eh_gen / voxel_volume / gen_time

    # convert distance units to meters
    x *= 1e-6
    y *= 1e-6
    z *= 1e-6

    return x, y, z, G  # TODO This is going to be very expensive, maybe pass as args

