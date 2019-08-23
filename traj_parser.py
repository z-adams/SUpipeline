from trajectory import Trajectory
import sys
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))

def separate_collisions(trajectories):
    """ Separates the list of trajectories by parent primary particle
    
    args:
    trajectories -- the list of all trajectories in the simulation
    
    returns a list of showers, i.e. a list of lists that each contain
    the primary and secondary trajectories resulting from each impact
    """
    showers = []  # list of lists of trajectories associated with a parent
    shower_index = -1  # will be incremented on first trajectory
    current_primary = 0
    for traj in trajectories:
        if traj.parent == 0:
            # new primary particle
            current_primary = traj.traj
            shower_index += 1
            showers.append([])  # create space for new shower
        # Assuming all child showers follow their primary
        showers[shower_index].append(traj)
    return showers

def parse_traj(filename, trim=True):
    """ Splits a .dat file from pyPENELOPE into a list of trajectories
    Assumes that lines with comments will contain only comments.

    args:
    filename -- the path of the .dat file
    trim -- removes extraneous data e.g. initial position, escaped particles

    returns a list of trajectories
    """
    logger.info("Parsing file '%s'", filename)

    # read raw file into buffer
    buf = []
    with open(filename, 'r') as f:
        for line in f:
            # skip comments
            if line.find('#') != -1:
                continue
            buf.append(line)
    logger.debug("File successfully read into buffer")

    # parse by traj
    num_lines = len(buf)
    i = 0
    trajectories = []
    while i < num_lines:
        line = buf[i]

        # parse header, begin new trajectory
        if line[0] == '0':
            logger.debug("Beginning new trajectory")
            # file ends with line of 00000000s, exit if at end
            if i == num_lines - 1:
                break

            info = []
            # header length is hardcoded (5 elements)
            for j in range(5):
                i += 1
                # take the number at the end of each header line and continue
                info.append(int(buf[i].split()[1]))
            logger.debug("Trajectory properties: %s", info)
            trajectories.append(
                    Trajectory(info[0], info[1], info[2], info[3], info[4]))
            i += 2 # skip over the '111111...' line to first line of data
            continue

        split = line.split()
        # Parse strings into values of appropriate type
        split = [float(j) for j in split[0:5]] + [int(k) for k in split[5:]]

        # Removes extraneous datapoints based on IBODY value
        if trim and split[5] != 1:
            logger.info("Deleting event #%d in trajectory %d: %s", i,
                    trajectories[-1].traj, split)
            i += 1
            continue


        # append event to event list
        trajectories[-1].events.append({
            "x": split[0],
            "y": split[1],
            "z": split[2],
            "E": split[3],
            "WGHT": split[4],
            "IBODY": split[5],
            "ICOL": split[6]})
        i += 1
    return trajectories

