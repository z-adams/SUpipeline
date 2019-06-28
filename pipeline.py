from lumerical import run_detector_test
from generation_rate import process_data
from penelope import run_penelope
import re
import time
import os
import shutil
## For now, single pyPENELOPE run with 10 e-, parse into individual files and
## run 10 lumerical simulations, yielding 10 refractive indices
# Considering threading using a work-stealing queue depending on hardware

def pause():
    try:
        raw_input("Press enter to continue...")
    except:
        pass

# TODO list
# more materials, configurations in pyPENELOPE
# charge density (generation_rate.py)
# lumerical settings?
# config file reading??
# multithreading?!??
# ?!??!??

# Constants
DATA_FILE_PATH = 'pe-trajectories.dat'

# Set up parameters
NUM_PARTICLES = 2
BEAM_ENERGY = 350e3  # It defaults to this but we'll define it here anyways
## Hardcoded in penelope.py for now:
# Material
# Energy params

# Invoke pyPENELOPE
run_penelope(NUM_PARTICLES, BEAM_ENERGY)

for i in range(10):
    if os.path.isfile(DATA_FILE_PATH):
        break
    time.sleep(1)
else:
    print >> sys.stderr, "could not find data file"

# Process scattering data, create .mat files
output_files = process_data(datafile=DATA_FILE_PATH, output_dir='./')

# Invoke Lumerical
# Obtain optical modulation from get_3D_n_matrix.lsf (also in lumerical.py)
for charge_file in output_files:
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    os.mkdir(filename)
    shutil.move(charge_file, "./{}/{}.mat".format(filename, filename))
    os.chdir(filename)
    out_file = "{}.ldev".format(filename)
    run_detector_test(charge_file, output_filename=out_file)
    os.chdir("..")

# Possibly plot using cal_ind_abs
