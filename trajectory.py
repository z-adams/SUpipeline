## Terminology:
 # Event - a single scattering event of the particle in the material
 # Trajectory - the list of events associated with a single particle
 # Shower - the trajectories of a primary particle and all its secondaries

# Events stored in a dict like so:
#event = {"x": x, "y": y, "z": z, "E": E, "WGHT": W, "IBODY": B, "ICOL": C}

# Example from a pe-trajectories.dat file:
"""
00000000000000000000000000000000000000000000000000000000000000000000000000000000
TRAJ          1  # A header like this begins a single trajectory
KPAR          1 
PARENT        0 <= "Parent" is 0 indicating that this trajectory is that of a
ICOL          0    primary particle, but secondary  trajs. would reference this
EXIT          1    one as their parent. The resulting group comprises a shower.
11111111111111111111111111111111111111111111111111111111111111111111111111111111
 -0.436428E-06 -0.990971E-07  0.100000E+02  0.350000E+06  0.100000E+01    2    0
 -0.436428E-06 -0.990971E-07  0.000000E+00  0.350000E+06  0.100000E+01    1    0
 -0.436428E-06 -0.990971E-07 -0.970348E-04  0.349556E+06  0.100000E+01    1    1
  0.146356E-05 -0.131129E-05 -0.137506E-03  0.349556E+06  0.100000E+01    1    5
  0.207338E-05 -0.170035E-05 -0.150496E-03  0.349556E+06  0.100000E+01    1    1
  0.166060E-04 -0.103876E-04 -0.230064E-03  0.349556E+06  0.100000E+01    1    5
  0.334916E-04 -0.204813E-04 -0.322514E-03  0.349556E+06  0.100000E+01    1    1
  0.642198E-04 -0.908017E-05 -0.417071E-03  0.349556E+06  0.100000E+01    1    5
  0.881949E-04 -0.184598E-06 -0.490848E-03  0.349556E+06  0.100000E+01    1    1
  ^ Each line is one "event" that makes up a single step in the trajectory
"""

class Trajectory:
    """ Represents a single trajectory and stores its list of events
    
    An event is a dict with the following keys:
    x -- x coordinate
    y -- y coordiante
    z -- z coordinate
    E -- Energy of particle
    Plus some indices describing the particles and type of collision involved
    """
    def __init__(self, TRAJ, KPAR, PARENT, ICOL, EXIT):
        self.traj = TRAJ
        self.kpar = KPAR
        self.parent = PARENT
        self.icol = ICOL
        self.exit = EXIT
        self.events = []

