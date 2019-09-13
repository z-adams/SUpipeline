import scipy.io as sio
import os
import logging
import numpy as np
from traj_parser import separate_collisions, parse_traj
from process_impact import process_impact
#from plot_dat import plot_dat
#from plot_traj import plot_traj
#from plot_both import plot_both

## This file calls a parser to process a pyPENELOPE .dat output file and
## translates the data into a volumetric measurement of the amount of energy
## deposited through the material by the electron, and writes a .mat matrix
## file for each electron shower on the material.

logger = logging.getLogger(os.path.basename(__file__))

def write_charge_gen_mat(x, y, z, G, filepath=None):
    """ Write a charge generation matrix to a .mat file
    Will prompt for a filepath to write to if none is provided.

    args:
    x, y, z -- the arrays of x, y, and z coordinates that form the voxel grid
    G -- the x*y*z matrix containing the volume charge data
    filepath -- the filename/location to save to

    returns nothing
    """
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
    """ Process a .dat file from pyPENELOPE into charge generation matrices

    args:
    datafile -- the .dat file of events (will prompt for path if None)
    output_dir -- the output directory to save to (will also prompt)
    plot -- if True, plots .dat and output data after each shower is processed
            - currently disabled

    returns a list of the output filenames
    """
    if datafile is None:
        # Get data file (currently prompting)
        logger.info("current location: %s", os.getcwd())
        datafile = raw_input("Where is the data?: ")

    # parse list of trajectories from pyPENELOPE, separate by parent primary
    logger.info("Parsing datafile '%s'", datafile)
    all_trajectories = parse_traj(datafile, trim=True)

    logger.debug("Parsing complete, separating trajectories")
    showers = separate_collisions(all_trajectories)

    output_files = []

    filename_template = "generation_{}.mat"
    if output_dir is None:
        output_dir = raw_input("Where should .mat files be saved?" \
                "\n(directory ending with '/'): ")  # linux CLI for now
    else:
        logger.debug("Using specified output_dir")

    for index, shower in enumerate(showers):
        # Process an shower (set of trajectories) and save charge generation info
        logger.debug("Processing shower #%d", index)
        x, y, z, G = process_impact(shower, N_grid=100)
        filepath = (output_dir + filename_template).format(index)
        logger.debug("Writing charge generation matrix to '%s'", filepath)
        write_charge_gen_mat(x, y, z, G, filepath=filepath)
        #if plot:
        #    plot_both(trajectories=shower, mat=filepath)
        output_files.append(filepath)
    return output_files

# If script is being run standalone
if __name__ == "__main__":
    process_data(plot=True)
