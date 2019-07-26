from lumerical import run_detector_test
from generation_rate import process_data
from traj_parser import parse_traj
from charge_density import compute_charge
from penelope import run_penelope
from argparse import ArgumentParser
import re
import time
import os
import shutil
import logging
from math import log10

### Arguments ###
# For more information about geometries and materials, see the README and
# penelope.py and lumerical.py files

# OPTIONS
USE_PENELOPE_FILE = False  # Use an existing pe-trajectories.dat file
RUN_LUMERICAL = False  # Running of lumerical can be disabled
WRITE_CHARGE_MAT = False  # Compute dense voxel matrix of charge generation
RUN_MANUAL_CHARGE = True  # Run approximate charge simulation scripts
RUN_FROM_SIM = 0  # start at the nth sim (0 == beginning)
RUN_TO_SIM = -1  # -1 to run to the last sim, else end at the nth
PURGE_LARGE_DATA = False  # Delete large files (.ldev, charge gen) after use
RUN_NTH_SIM = -1 # If not less than zero, run only the nth lumerical sim

# PARAMETERS
NUM_PARTICLES = 100
INCLUDE_SECONDARIES = False
BEAM_ENERGY = 350e3
PEN_MATERIALS = [
        {'name': 'CdTe', 'density': 5.85,
    'elements': [('Cd', 0.5), ('Te', 0.5)]}
    ]
#GEOMETRY = {'type': 1, 'layers': [('vacuum', -1), ('CdTe', 0.2)]}
GEOMETRY = {'type': 0, 'material': 'CdTe'}
LUM_MAT = "CdTe (Cadmium Telluride)"
LUM_MESH = {'min': 1e-6, 'max': 1e-5}
LUM_RESULTS = {'free_charge': False, 'space_charge': False}

##### You shouldn't need to touch anything below this line #####

def build_parameters(num_particles=None, include_secondaries=None,
        beam_energy=None, pen_materials=None, geometry=None, lum_mat=None,
        lum_mesh=None, lum_results=None):

    args = (num_particles, include_secondaries, beam_energy, pen_materials,
            geometry, lum_mat, lum_mesh, lum_results)

    # Error checking parameters
    if None in args:
        logger.error("Error building parameter dict from function arguments,"\
                " missing args: %s", [e for e in args if e is None])
        return None

    params = {'NUM_PARTICLES': num_particles,
            'INCLUDE_SECONDARIES': include_secondaries,
            'BEAM_ENERGY': beam_energy, 'PEN_MATERIALS': pen_materials,
            'GEOMETRY': geometry, 'LUM_MAT': lum_mat, 'LUM_MESH': lum_mesh,
            'LUM_RESULTS': lum_results}
    return params

def build_options(use_penelope_file=None, run_lumerical=None,
        write_charge_mat=None, run_manual_charge=None, run_from_sim=None,
        run_to_sim=None, purge_large_data=None, run_nth_sim=None):
     
    args = (use_penelope_file, run_lumerical, write_charge_mat,
            run_manual_charge, run_from_sim, run_to_sim,
            purge_large_data, run_nth_sim)

    # Error checking options
    if None in args:
        logger.error("Error building parameter dict from function arguments,"\
                " missing args: %s", [e for e in args if e is None])
        return None
    if run_to_sim > 0 and run_to_sim < run_from_sim:
        logger.critical("RUN_TO_SIM must be larger than RUN_FROM_SIM")
        return None

    options = {'USE_PENELOPE_FILE': use_penelope_file, 
            'RUN_LUMERICAL': run_lumerical,
            'WRITE_CHARGE_MAT': write_charge_mat,
            'RUN_MANUAL_CHARGE': run_manual_charge,
            'RUN_FROM_SIM': run_from_sim,
            'RUN_TO_SIM': run_to_sim,
            'PURGE_LARGE_DATA': purge_large_data, 
            'RUN_NTH_SIM': run_nth_sim}
    return options

# Create set of default parameters and options

def default_parameters():
    return build_parameters(num_particles=1,
            beam_energy=350e3,
            include_secondaries=False,
            pen_materials=[{'name': 'CdTe', 'density': 5.85,
                'elements': [('Cd', 0.5), ('Te', 0.5)]}],
            geometry={'type': 0, 'material': 'CdTe'},
            lum_mat="CdTe (Cadmium Telluride)",
            lum_mesh={'min': 1e-6, 'max': 1e-5},
            lum_results={'free_charge': False, 'space_charge': False}
            )

def default_options():
    return build_options(use_penelope_file=False, run_lumerical=False,
            write_charge_mat=False, run_manual_charge=True, run_from_sim=0,
            run_to_sim=-1, purge_large_data=True, run_nth_sim=-1)


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
    if loglevel is not None:
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

def get_file_number(filename):
    return re.search(r'(\d+(?=.mat))', filename).group(0)

# Finds the index of a file with a given number in a list
# Example:
# >> find_file_number_in_lits(3, ['gen_2.mat', 'gen_3.mat', 'gen_4.mat']
# returns 1, the index of gen_3.mat in the list
def find_file_number_in_list(number, file_list):
    indices = [index for index, name in enumerate(file_list) 
            if int(re.search(r'(\d+(?=.mat))', name).group(0)) == number]
    if not indices:
        return None
    if indices[0] is not indices[-1]:
        logger.warning("find_file_number_in_list found more than one match "\
                "for %d in %s", number, file_list)
    return indices[0]

def configure_and_run_lumerical(charge_file, params, options, scripts=None):
    # Configure simulation workspace
    filename = re.split(r'[/\\]', charge_file)  # strip preceeding path
    filename = re.sub(r'[\.]\w+', '', filename[-1])  # strip file extension
    if os.path.isdir(filename):
        logger.warn("Directory '%s' already exists, skipping sim", filename)
        return
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
            scripts=scripts
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

    if scripts is not None:
        SCRIPTS.extend(scripts)

    # Determine if the directory structure is already set up
    if all(folder in os.listdir('.') 
            for folder in ["pyPENELOPE", "results", "scripts"]):
        logger.info("Existing directory structure detected, resuming")
        STRUCTURE_EXISTS = True
    else:
        STRUCTURE_EXISTS = False

    if STRUCTURE_EXISTS is False:
        # Set up directories, find .lsf files and move into ./scripts
        os.mkdir("pyPENELOPE")
        os.mkdir("results")
        os.mkdir("scripts")
        dirlist = os.listdir('.')
        logger.debug('dirlist: %s', dirlist)

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
    else:
        for f in os.listdir('scripts'):
            if ".lsf" in f:
                logger.debug("found .lsf file '%s' in scripts/", f)
                SCRIPTS.append("../../scripts/{}".format(f))
        if DATA_FILE_PATH.split("/")[-1] in os.listdir('pyPENELOPE'):
            logger.info("found data file '%s' in pyPENELOPE/",
                    DATA_FILE_PATH.split('/')[-1])

    logger.info("Found SCRIPTS: %s", SCRIPTS)

    # Invoke pyPENELOPE
    if not STRUCTURE_EXISTS and not USE_PENELOPE_FILE:
        os.chdir("pyPENELOPE")
        logger.info("Running pyPENELOPE...")
        run_penelope(num_particles=params['NUM_PARTICLES'],
                beam_energy=params['BEAM_ENERGY'],
                materials=params['PEN_MATERIALS'],
                geometry=params['GEOMETRY'],
                secondaries=params['INCLUDE_SECONDARIES'])

        # Writing results from longer sims takes longer
        wait = int(10 + 10*log10(params['NUM_PARTICLES']))
        logger.info("Allowing %s seconds for data file to be written", wait)
        for i in range(wait):
            if os.path.isfile(DATA_FILE_PATH.split('/')[-1]):
                logger.info("PENELOPE output file found")
                break
            time.sleep(1)
        else:
            logger.warning("Data file was not produced")
        os.chdir("..")
    else:
        logger.info("Skipping pyPENELOPE simulation, using found data file")

    # Write charge generation matrices
    if options['WRITE_CHARGE_MAT']:
        # Process scattering data, create .mat files
        os.chdir("results")
        if STRUCTURE_EXISTS:
            logger.debug("Dirlist: %s", os.listdir('.'))
            output_files = [f for f in os.listdir('.') if ".mat" in f]
            logger.debug("Detected .mat files: %s", output_files)
            output_files.sort(
                    key=lambda x:int(re.search(r'(\d+(?=.mat))', x).group(0)))
        else:
            output_files = process_data(datafile=DATA_FILE_PATH, output_dir='./')
        logger.debug("output files discovered: '%s'", output_files)

    # Manually compute charge transport
    if options['RUN_MANUAL_CHARGE']:
        os.chdir("results")
        output = ["### Final Charge Densities ###", 
                str(options), str(params), 
                "##############################",
                "Traj #:\t\tDensity:"]
        if params['INCLUDE_SECONDARIES']:
            logger.warning("Manual charge does not support secondary " \
                    "particles, weird behavior will result")
        trajectories = parse_traj(DATA_FILE_PATH)
        if options['RUN_NTH_SIM'] >= 0:
            start = options['RUN_NTH_SIM']
            end = start + 1
        else:
            from_sim = options['RUN_FROM_SIM']
            to_sim = options['RUN_TO_SIM']
            if to_sim < 0:
                to_sim = len(trajectories)

        for i in range(from_sim, to_sim):
            density = compute_charge(trajectories[i])
            output.append("{0:d}:\t\t{1:.9e}".format(i, density))

        with open("n.txt", "w") as data_output:
            for line in output:
                data_output.write("{}\n".format(line))

    # Run lumerical on charge generation matrices
    if options['RUN_LUMERICAL'] == True:
        ## Options for running select simulations
        # Running one specific simulation
        if (options['RUN_NTH_SIM'] >= 0):
            i = find_file_number_in_list(options['RUN_NTH_SIM'], output_files)
            logger.info("Running lumerical on single file '%s'", output_files[i])
            configure_and_run_lumerical(output_files[i], params, options, SCRIPTS)
        else:
        # Running a range of simulations
            from_sim = options['RUN_FROM_SIM']
            to_sim = options['RUN_TO_SIM']
            if from_sim < 1 and to_sim < 0:
                message = "Running lumerical on all files"
            else:
                from_index = find_file_number_in_list(from_sim, output_files)
                msg_from_sim = output_files[from_index]
                if to_sim < 0:
                    msg_to_sim = output_files[-1]
                else:
                    to_index = find_file_number_in_list(to_sim, output_files)
                    msg_to_sim = output_files[to_index]
                message = "Running lumerical on trajectories {} " \
                        "through {}".format(msg_from_sim, msg_to_sim)
                logger.info(message)

            # Invoke Lumerical, call .lsf script to get optical modulation
            for charge_file in output_files:

                # Since we can start at any file, we need to know the index of the
                # file itself, not the index of the file in output_files
                file_index = int(re.search(r'(\d+(?=.mat))',
                    charge_file).group(0))

                # Skip until starting point
                if file_index < from_sim:
                    continue
                elif file_index == from_sim:
                    logger.info("Beginning from sim #%d", file_index)

                # Break if ending point reached
                if to_sim > 0 and file_index > to_sim:
                    logger.info("Hit maximum simulations: quitting")
                    break

                # Run simulation
                configure_and_run_lumerical(charge_file, params, options, SCRIPTS)

if __name__ == '__main__':
    # If this script is main, we can assume user wants to use local parameters
    logger.info("Program is __main__")
    logger.info("Building local parameters")
    LOCAL_PARAMS = build_parameters(
            num_particles=NUM_PARTICLES,
            include_secondaries=INCLUDE_SECONDARIES,
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
            run_lumerical=RUN_LUMERICAL,
            write_charge_mat=WRITE_CHARGE_MAT,
            run_manual_charge=RUN_MANUAL_CHARGE,
            run_from_sim=RUN_FROM_SIM,
            run_to_sim=RUN_TO_SIM,
            purge_large_data=PURGE_LARGE_DATA,
            run_nth_sim=RUN_NTH_SIM
            )

    logger.info("Running pipeline")
    run_pipeline(params=LOCAL_PARAMS, options=LOCAL_OPTIONS)
