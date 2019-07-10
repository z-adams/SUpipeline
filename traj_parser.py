import sys
import logging
import os

logger = logging.getLogger(os.path.basename(__file__))

class Trajectory:
    """ Represents a single trajectory and stores its list of events"""
    def __init__(self, TRAJ, KPAR, PARENT, ICOL, EXIT):
        self.traj = TRAJ
        self.kpar = KPAR
        self.parent = PARENT
        self.icol = ICOL
        self.exit = EXIT
        self.events = []

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
        # Parse strings into appropriate values
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

