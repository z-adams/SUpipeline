import sys

class Trajectory:
    def __init__(self, TRAJ, KPAR, PARENT, ICOL, EXIT):
        self.traj = TRAJ
        self.kpar = KPAR
        self.parent = PARENT
        self.icol = ICOL
        self.exit = EXIT
        self.events = []

################### PARSER ####################
# Naive split of file into list of trajectories, which is then returned.
# Assumptions: lines with comments will contain only comments
# Special considerations:
# first event contains the initial position and energy of the incident particle
# 
def parse(filename, trim=False):
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
    trajectories = []
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

        split = line.split()
        # Parse strings into appropriate values
        split = [float(j) for j in split[0:5]] + [int(k) for k in split[5:]]

        #LIM = 1  # value past which we can exclude a datapoint from the set
        # Remove incident event so it doesn't cause problems later:
        #if trim and any(e > LIM for e in [split[0], split[1], split[2]]):
        #    print >> sys.stderr, "Delete evt #{} in traj {}: " \
        #    "{}".format(i, trajectories[-1].traj, split)
        #    i += 1
        #    continue

        # experimental: this seems like it will work TODO validate
        if trim and split[5] != 1:
            print >> sys.stderr, "Delete evt #{} in traj {}: " \
            "{}".format(i, trajectories[-1].traj, split)
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
        #debug:
        #event = trajectories[-1].events[-1]
        #print "({},{},{})".format(event["x"], event["y"], event["z"])
        i += 1
    return trajectories

