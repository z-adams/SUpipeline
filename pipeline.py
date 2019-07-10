from lumerical import run_detector_test
from generation_rate import process_data
from penelope import run_penelope
from argparse import ArgumentParser
import re
import time
import os
import shutil
import logging

### Arguments ###
# For more information about geometries and materials, see the README and
# penelope.py and lumerical.py files

# OPTIONS
USE_PENELOPE_FILE = False  # Use an existing pe-trajectories.dat file
LUM_SIM_LIMIT = -1  # -1 to simulate all trajectories, n to limit runs
PURGE_LARGE_DATA = True  # Delete large files (.ldev, charge gen) after use
RUN_NTH_SIM = -1  # If not less than zero, run only the nth lumerical sim

# PARAMETERS
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

##### You shouldn't need to touch anything below this line #####

def build_parameters(num_particles=None, beam_energy=None, pen_materials=None,
        geometry=None, lum_mat=None, lum_mesh=None, lum_results=None):

    args = (num_particles, beam_energy, pen_materials, geometry, lum_mat,
            lum_mesh, lum_results)

    if None in args:
        logger.error("Error building parameter dict from function arguments,"\
                " missing args: %s", [e for e in args if e is None])
        return None

    params = {'NUM_PARTICLES': num_particles, 'BEAM_ENERGY': beam_energy, 
        'PEN_MATERIALS': pen_materials, 'GEOMETRY': geometry,
        'LUM_MAT': lum_mat, 'LUM_MESH': lum_mesh, 'LUM_RESULTS': lum_results}
    return params

def build_options(use_penelope_file=None, lum_sim_limit=None,
        purge_large_data=None, run_nth_sim=None):
     
    args = (use_penelope_file, lum_sim_limit, purge_large_data, run_nth_sim)

    if None in args:
        logger.error("Error building parameter dict from function arguments,"\
                " missing args: %s", [e for e in args if e is None])
        return None

    options = {'USE_PENELOPE_FILE': use_penelope_file, 
        'LUM_SIM_LIMIT': lum_sim_limit, 'PURGE_LARGE_DATA': purge_large_data, 
        'RUN_NTH_SIM': run_nth_sim}
    return options

# Create set of default parameters and options

def default_parameters():
    return build_parameters(num_particles=1,
            beam_energy=350e3,
            pen_materials=[{'name': 'CdTe', 'density': 5.85,
                'elements': [('Cd', 0.5), ('Te', 0.5)]}],
            geometry={'type': 0, 'material': 'CdTe'},
            lum_mat="CdTe (Cadmium Telluride)",
            lum_mesh={'min': 1e-6, 'max': 1e-5},
            lum_results={'free_charge': False, 'space_charge': False}
            )

def default_options():
    return build_options(use_penelope_file=False, lum_sim_limit=-1, 
            purge_large_data=True, run_nth_sim=-1)



DEFAULT_PARAMS = default_parameters()
DEFAULT_OPTIONS = default_options()

DATA_FILE_PATH = '../pyPENELOPE/pe-trajectories.dat'

# Logging command line arg (--log=...)
# There's another (actual) 'main' at the bottom of the file
if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--log", 
            help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    loglevel = arg_parser.parse_args().log
    numeric_level= getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level')
    logging.basicConfig(level=numeric_level)
logger = logging.getLogger(os.path.basename(__file__))

# Can be useful for debugging
def pause():
    try:
        raw_input("Press enter to continue...")
    except:
        pass

def configure_and_run_lumerical(charge_file, params, options):
    # Configure simulation workspace
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    logger.debug("creating directory for file: %s", filename)
    os.mkdir(filename)
    shutil.move(charge_file, "./{}/{}.mat".format(filename, filename))
    os.chdir(filename)
    out_file = "{}.ldev".format(filename)

    logger.debug("Running lumerical on %s", charge_file)
    run_detector_test(charge_file,
            material=params['LUM_MAT'],
            mesh_options=params['LUM_MESH'],
            results=params['LUM_RESULTS'],
            output_filename=out_file, 
            scripts=SCRIPTS
            )

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

def run_pipeline(params=DEFAULT_PARAMS, options=DEFAULT_OPTIONS, scripts=None):

    SCRIPTS = []

    if (logger.getEffectiveLevel() < 30):  # If logging info/debug
        logger.info("########## PARAMETERS ##########")
        for key in params:
            logger.info("{}: {}".format(key, params[key]))
        logger.info("##########  OPTIONS   ##########")
        for key in options:
            logger.info("{}: {}".format(key, options[key]))

    # Set up directories, find .lsf files and move into ./scripts
    os.mkdir("pyPENELOPE")
    os.mkdir("results")
    os.mkdir("scripts")
    dirlist = os.listdir('.')
    logger.debug('dirlist: %s', dirlist)

    if scripts is not None:
        SCRIPTS.extend(scripts)

    if (options['USE_PENELOPE_FILE'] and 
            DATA_FILE_PATH.split("/")[-1] not in dirlist):
        raise IOError("Data file not found!")
    for f in dirlist:
        if ".lsf" in f:
            logger.debug("found .lsf file '%s'", f)
            SCRIPTS.append("../../scripts/{}".format(f))
            shutil.move(f, "./scripts/{}".format(f))
        if DATA_FILE_PATH.split("/")[-1] in f:
            logger.info("found data file '%s' in dir",
                    DATA_FILE_PATH.split('/')[-1])
            shutil.move(f, "./pyPENELOPE/{}".format(f))

    logger.info("Found SCRIPTS: %s", SCRIPTS)

    # Invoke pyPENELOPE
    if not USE_PENELOPE_FILE:
        os.chdir("pyPENELOPE")
        logger.info("Running pyPENELOPE...")
        run_penelope(params['NUM_PARTICLES'], params['BEAM_ENERGY'],
                params['PEN_MATERIALS'], params['GEOMETRY'])

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

    if (options['RUN_NTH_SIM'] > 0):
        logger.info("Running lumerical on single file '%s'", 
                output_files[options['RUN_NTH_SIM']])
        configure_and_run_lumerical(
                output_files[options['RUN_NTH_SIM']], params, options)
    else:
        if LUM_SIM_LIMIT > 0:
            logger.info("Running lumerical on first '%s' files")
        else:
            logger.info("Running lumerical on all files")
        # Invoke Lumerical, call .lsf script to get optical modulation
        for index, charge_file in enumerate(output_files):

            # limit number of trajectories to simulate
            sim_limit = options['LUM_SIM_LIMIT']
            if sim_limit > 0 and index > sim_limit:
                logger.info("Hit maximum simulations: quitting")
                break
            configure_and_run_lumerical(charge_file, params, options)

if __name__ == '__main__':
    # If this script is main, we can assume user wants to use local parameters
    logger.info("Program is __main__")
    logger.info("Building local parameters")
    LOCAL_PARAMS = build_parameters(
            num_particles=NUM_PARTICLES,
            beam_energy=BEAM_ENERGY,
            pen_materials=PEN_MATERIALS,
            geometry=GEOMETRY,
            lum_mat=LUM_MAT,
            lum_mesh=LUM_MESH,
            lum_results=LUM_RESULTS
            )
    logger.info("Building local options") 
    LOCAL_OPTIONS = build_options(
            use_penelope_file=USE_PENELOPE_FILE,
            lum_sim_limit=LUM_SIM_LIMIT,
            purge_large_data=PURGE_LARGE_DATA,
            run_nth_sim=RUN_NTH_SIM
            )

    logger.info("Running pipeline")
    run_pipeline(params=LOCAL_PARAMS, options=LOCAL_OPTIONS)
