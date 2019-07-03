from lumerical import run_detector_test
from generation_rate import process_data
from penelope import run_penelope
import re
import time
import os
import shutil
# Considering threading using a work-stealing queue depending on hardware

def pause():
    try:
        raw_input("Press enter to continue...")
    except:
        pass

# Directory structure:
# Root
#|-- pyPENELOPE
#|   |-- pe-trajectories.dat
#|   +-- other PENELOPE output (materials, geometry, etc)
#|-- scipts
#|   |-- get_3D_n_matrix.lsf
#|   +-- any other script files
#|-- results
#|   |-- generation_0
#|   |   |-- generation_0.mat
#|   |   |-- generation_0.ldev
#|   |   |-- charge.mat
#|   |   +-- abs,x,y,z_rect.mat (n data)
#|   ...
#|   |
#|   +-- generation_n
#|       |-- generation_n.mat, .ldev
#|       +-- ...

# TODO list
# more materials, configurations in pyPENELOPE  CHECK
# charge density (generation_rate.py)
# lumerical settings? (mesh [CHECK], convergence, transience?)
# config file reading??
# multithreading?!??
# ?!??!??

# Constants
DATA_FILE_PATH = '../pyPENELOPE/pe-trajectories.dat'
USE_PENELOPE_FILE = False
LUM_SIM_LIMIT = -1 # -1 to simulate all trajectories, n to limit runs

# Set up parameters
NUM_PARTICLES = 100
BEAM_ENERGY = 350e3
PEN_MATERIALS = [
        {'name': 'CdTe', 'density': 5.85,
    'elements': [('Cd', 0.5), ('Te', 0.5)]}
    ]
GEOMETRY = {'type': 1, 'layers': [('vacuum', -1), ('CdTe', 0.2)]}
LUM_MAT = "CdTe (Cadmium Telluride)"
LUM_MESH = {'min': 1e-6, 'max': 1e-5}
LUM_RESULTS = {'free_charge': False, 'space_charge': False}
SCRIPTS = []

# Set up directories, find .lsf files and move into ./scripts
os.mkdir("pyPENELOPE")
os.mkdir("results")
os.mkdir("scripts")
dirlist = os.listdir('.')
if USE_PENELOPE_FILE and DATA_FILE_PATH.split("/")[-1] not in dirlist:
    raise IOError("Data file not found!")
for f in dirlist:
    if ".lsf" in f:
        SCRIPTS.append("../../scripts/{}".format(f))
        shutil.move(f, "./scripts/{}".format(f))
    if DATA_FILE_PATH.split("/")[-1] in f:
        shutil.move(f, "./pyPENELOPE/{}".format(f))
        print "Using found data file"

# Invoke pyPENELOPE
if not USE_PENELOPE_FILE:
    os.chdir("pyPENELOPE")
    run_penelope(NUM_PARTICLES, BEAM_ENERGY, PEN_MATERIALS, GEOMETRY)

    for i in range(10):
        if os.path.isfile(DATA_FILE_PATH):
            break
        time.sleep(1)
    else:
        print >> sys.stderr, "data file was not produced"
    os.chdir("..")

# Process scattering data, create .mat files
os.chdir("results")
output_files = process_data(datafile=DATA_FILE_PATH, output_dir='./')

# Invoke Lumerical, call .lsf script to get optical modulation
for index, charge_file in enumerate(output_files):

    # limit number of trajectories to simulate
    if LUM_SIM_LIMIT > 0 and index > LUM_SIM_LIMIT:
        break

    # Configure simulation workspace
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    os.mkdir(filename)
    shutil.move(charge_file, "./{}/{}.mat".format(filename, filename))
    os.chdir(filename)
    out_file = "{}.ldev".format(filename)

    run_detector_test(charge_file, material=LUM_MAT, mesh_options=LUM_MESH,
            results=LUM_RESULTS, output_filename=out_file, 
            scripts=SCRIPTS)
    os.chdir("..")

# Possibly plot using cal_ind_abs
