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

# TODO: add more organization of files

# Set up parameters
NUM_PARTICLES = 2
BEAM_ENERGY = 350e3  # It defaults to this but we'll define it here anyways
## Hardcoded in penelope.py for now:
# Material
# Energy params

# Invoke pyPENELOPE
run_penelope(NUM_PARTICLES, BEAM_ENERGY)

time.sleep(10)  # TODO HACK (needs some time for .dat to be created)
#try:
#    raw_input("press any key to continue...")
#except:
#    pass
# Process scattering data, create .mat files
output_files = process_data(datafile='pe-trajectories.dat', output_dir='./')
#try:
#    raw_input("press any key to continue...")
#except:
#    pass
# Invoke Lumerical
for charge_file in output_files:
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    os.mkdir(filename)
    shutil.move(charge_file, "./{}/{}.mat".format(filename, filename))
    os.chdir(filename)
    out_file = "{}.ldev".format(filename)
    run_detector_test(charge_file, output_filename=out_file)
    os.chdir("..")

# Obtain optical modulation from get_3D_n_matrix.lsf

# Possibly plot using cal_ind_abs
