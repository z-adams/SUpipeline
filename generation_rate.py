import scipy.io as sio
import os
import numpy as np
from parser import *
from process_impact import process_impact
from plot_dat import plot_dat
from plot_traj import plot_traj
from plot_both import plot_both

## This file calls a parser to process a pyPENELOPE .dat output file and
## translates the data into a volumetric measurement of the amount of energy
## deposited through the material by the electron, and writes a .mat matrix
## file for each electron incident on the material.

## Terminology:
 # Event - a single scattering event of the particle in the material
 # Trajectory - the list of events associated with a single particle
 # Incident - the trajectories of a primary particle and all its secondaries

# Events stored in a dict like so:
#event = {"x": x, "y": y, "z": z, "E": E, "WGHT": W, "IBODY": B, "ICOL": C}

# All n events from the simulation are in one big list and need to be separated
# into a list of trajectories.
# "Parent" attribute of each trajectory allow for sorting. Trajectories are
# (thankfully) sorted so secondary particles follow their parent primary.
def separate_collisions(trajectories):
    incidents = []  # list of lists of trajectories associated with a parent
    inc_index = -1  # will be incremented on first trajectory
    current_primary = 0
    for traj in trajectories:
        if traj.parent == 0:
            # new primary particle
            current_primary = traj.traj
            inc_index += 1
            incidents.append([])  # create space for new incident
        elif traj.parent != current_primary:
            print >> sys.stderr, "weird trajectory ordering"
        incidents[inc_index].append(traj)
    return incidents

# Write a charge generation matrix to a file. Will prompt for a filepath to
# write to if none is provided.
def write_charge_gen_mat(x, y, z, G, filepath=None):
    # Matlab arrays are 2D "column vectors" with shape (1, m)
    # Here I transpose them to be 1 column of m (-1: automatic) elements
    np.reshape(x, (1, -1))
    np.reshape(y, (1, -1))
    np.reshape(z, (1, -1))
    data = {"x": x, "y": y, "z": z, "G": G}
    if filepath is None:
        mat = raw_input("Where should I save the data?: ")
        sio.savemat(mat, data)
    else:
        sio.savemat(filepath, data)

def process_data(datafile=None, output_dir=None, plot=False):
    if datafile is None:
        # Get data file (currently prompting)
        print "current location: {}".format(os.getcwd())
        datafile = raw_input("Where is the data?: ")

    # parse list of trajectories from pyPENELOPE, separate by parent primary
    all_trajectories = parse(datafile, trim=True)
    incidents = separate_collisions(all_trajectories)

    output_files = []

    filename_template = "generation_{}.mat"
    if output_dir is None:
        output_dir = raw_input("Where should .mat files be saved?" \
                "\n(directory ending with '/'): ")  # linux CLI for now

    for index, incident in enumerate(incidents):
        # Process an incident (set of trajectories) and save charge generation info
        x, y, z, G = process_impact(incident, N_grid=100)
        filepath = (output_dir + filename_template).format(index)
        write_charge_gen_mat(x, y, z, G, filepath=filepath)
        if plot:
            #plot_dat(trajectories=incident)
            #plot_traj(filename=filepath)
            plot_both(trajectories=incident, mat=filepath)
        output_files.append(filepath)
    return output_files

# If script is being run standalone
if __name__ == "__main__":
    process_data(plot=True)
