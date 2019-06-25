
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
def parse(filename):
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
        #debug:
        #event = trajectories[-1].events[-1]
        #print "({},{},{})".format(event["x"], event["y"], event["z"])
        i += 1
    return trajectories

