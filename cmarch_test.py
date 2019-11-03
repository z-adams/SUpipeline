from marchlib.pymarch import run_raymarcher
from marchlib.visualize import plot
from charge_density import compute_charge
from traj_parser import parse_traj
import numpy as np
import matplotlib.pyplot as plt

trajs = parse_traj("pe-trajectories.dat")

volumes = []
compute_charge(trajs[0], volumes)

resolution = 4e-7  # [m]
projection = "XY"

data = run_raymarcher(volumes, resolution, projection)

#plot("/marchlib/output.txt")
#plasma_r
plt.imshow(data, cmap="plasma", vmin=-1e-13, vmax=1e20)
plt.colorbar()
plt.show()
