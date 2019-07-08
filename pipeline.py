from lumerical import run_detector_test
from generation_rate import process_data
from penelope import run_penelope
from argparse import ArgumentParser
import re
import time
import os
import shutil
import logging
# Considering threading using a work-stealing queue depending on hardware

arg_parser = ArgumentParser()
arg_parser.add_argument("--log", 
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
loglevel = arg_parser.parse_args().log
numeric_level= getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level')
logging.basicConfig(level=numeric_level)
logger = logging.getLogger(os.path.basename(__file__))

# Constants
USE_PENELOPE_FILE = False
LUM_SIM_LIMIT = -1  # -1 to simulate all trajectories, n to limit runs
PURGE_LARGE_DATA = True  # Delete large files (.ldev, charge gen) after use
RUN_NTH_SIM = -1  # If not less than zero, run only the nth lumerical sim

# Set up parameters
NUM_PARTICLES = 2
BEAM_ENERGY = 350e3
PEN_MATERIALS = [
        {'name': 'CdTe', 'density': 5.85,
    'elements': [('Cd', 0.5), ('Te', 0.5)]}
    ]
GEOMETRY = {'type': 1, 'layers': [('vacuum', -1), ('CdTe', 0.2)]}
LUM_MAT = "CdTe (Cadmium Telluride)"
LUM_MESH = {'min': 1e-6, 'max': 1e-5}
LUM_RESULTS = {'free_charge': False, 'space_charge': False}

# Don't touch
DATA_FILE_PATH = '../pyPENELOPE/pe-trajectories.dat'
SCRIPTS = []

def pause():
    try:
        raw_input("Press enter to continue...")
    except:
        pass

def configure_and_run_lumerical(charge_file):
    # Configure simulation workspace
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    logger.debug("creating directory for file: %s", filename)
    os.mkdir(filename)
    shutil.move(charge_file, "./{}/{}.mat".format(filename, filename))
    os.chdir(filename)
    out_file = "{}.ldev".format(filename)

    logger.debug("Running lumerical on %s", charge_file)
    run_detector_test(charge_file, material=LUM_MAT, mesh_options=LUM_MESH,
            results=LUM_RESULTS, output_filename=out_file, 
            scripts=SCRIPTS)

    # Clean up directory
    if PURGE_LARGE_DATA:
        logger.info("Purging large data files")
        os.remove("{}.mat".format(filename))
        os.remove("{}.ldev".format(filename))
    os.chdir("..")

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

PARAMS = {'DATA_FILE_PATH': DATA_FILE_PATH, 
        'USE_PENELOPE_FILE': USE_PENELOPE_FILE, 'LUM_SIM_LIMIT': LUM_SIM_LIMIT,
        'PURGE_LARGE_DATA': PURGE_LARGE_DATA, 'RUN_NTH_SIM': RUN_NTH_SIM,
        'NUM_PARTICLES': NUM_PARTICLES, 'BEAM_ENERGY': BEAM_ENERGY,
        'PEN_MATERIALS': PEN_MATERIALS, 'GEOMETRY': GEOMETRY,
        'LUM_MAT': LUM_MAT, 'LUM_MESH': LUM_MESH, 'LUM_RESULTS': LUM_RESULTS}

if (logger.getEffectiveLevel() < 30):  # If logger info/debug
    logger.info("########## PARAMETERS ##########")
    for key in PARAMS:
        logger.info("{}: {}".format(key, PARAMS[key]))

# Set up directories, find .lsf files and move into ./scripts
os.mkdir("pyPENELOPE")
os.mkdir("results")
os.mkdir("scripts")
dirlist = os.listdir('.')
logger.debug('dirlist: %s', dirlist)

if USE_PENELOPE_FILE and DATA_FILE_PATH.split("/")[-1] not in dirlist:
    raise IOError("Data file not found!")
for f in dirlist:
    if ".lsf" in f:
        logger.debug("found .lsf file '%s'", f)
        SCRIPTS.append("../../scripts/{}".format(f))
        shutil.move(f, "./scripts/{}".format(f))
    if DATA_FILE_PATH.split("/")[-1] in f:
        logger.info("found data file '%s' in dir", DATA_FILE_PATH.split('/')[-1])
        shutil.move(f, "./pyPENELOPE/{}".format(f))

logger.info("SCRIPTS: %s", SCRIPTS)

# Invoke pyPENELOPE
if not USE_PENELOPE_FILE:
    os.chdir("pyPENELOPE")
    logger.info("Running pyPENELOPE...")
    run_penelope(NUM_PARTICLES, BEAM_ENERGY, PEN_MATERIALS, GEOMETRY)

    for i in range(10):
        if os.path.isfile(DATA_FILE_PATH.split('/')[-1]):
            logger.info("PENELOPE output file found")
            break
        time.sleep(1)
    else:
        logger.warning("Data file was not produced")
    os.chdir("..")
else:
    logger.info("Skipping pyPENELOPE simulation, using found data file")

# Process scattering data, create .mat files
os.chdir("results")
output_files = process_data(datafile=DATA_FILE_PATH, output_dir='./')
logger.debug("output files discovered: '%s'", output_files)

if (RUN_NTH_SIM > 0):
    logger.info("Running lumerical on single file '%s'", 
            output_files[RUN_NTH_SIM])
    configure_and_run_lumerical(output_files[RUN_NTH_SIM])
else:
    if LUM_SIM_LIMIT > 0:
        logger.info("Running lumerical on first '%s' files")
    else:
        logger.info("Running lumerical on all files")
    # Invoke Lumerical, call .lsf script to get optical modulation
    for index, charge_file in enumerate(output_files):

        # limit number of trajectories to simulate
        if LUM_SIM_LIMIT > 0 and index > LUM_SIM_LIMIT:
            logger.info("Hit maximum simulations: quitting")
            break
        configure_and_run_lumerical(charge_file)

# Possibly plot using cal_ind_abs

