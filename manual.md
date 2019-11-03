## Pipeline

### Hierarchy

The components listed approximately from lower to higher level - 
later files are less fundamental.

* `penelope.py`
    * `def run_penelope(...)`: Bypasses the penelope GUI and calls the
pyPENELOPE API directly to run penelope in the CWD

* `lumerical.py`
    * `def run_detector_test(...)`: Calls the Lumerical python API to build
a simulation volume around a generation rate matrix and run a charge transport
simulation.

* `trajectory.py`
    * `class Trajectory`: Contains the description of a "trajectory" object,
used to store pyPENELOPE trajectories in memory. Its members are the properties
of the trajectory, as well as a list containing the trajectory's events.

* `traj_parser.py`
    * `def parse_traj(filename, trim=True)`: Used to parse
`pe-trajectories.dat` files from pyPENLOPE into a list of `Trajectory`
objects. Has the option to trim extraneous datapoints based on IBODY value.
    * `def separate_collisions(trajectories)`: Used to separate a list of
trajectory objects by primary particle, resulting in a list of "showers" that
each were caused by a single primary.

* `process_impact.py`
    * `def preprocess_data(trajectories)`: Scans the trajectories for minimum
and maximum values to later be used to adjust the simulation volume
    * `def deltaX(event0, event1)`: Compute the distance between two points
    * `def process_impact(trajectories, N_grid)`: Compute charge generation
due to a shower of trajectories, with a given bin side length

* `charge_density.py`
    * `def compute_charge(trajectory, volumes=None)`: Compute the charge density
resulting from a trajectory, using a simple equation to approximate charge
diffusion. Has the ability to output a list of charge clouds (volumes), storing
spatial information along with the radius and density of each cloud, for more
detailed processing.

* `plot_dat.py` and `plot_traj.py`: Used to plot `pe-trajectories.dat` files
and Lumerical generation rate `.mat` files, respectively, using matplotlib.

* `generation_rate.py`
    * `def process_data(...)`: processes a `pe-trajectories.dat` file into
charge generation matrices, to be fed to Lumerical.

* `pipeline.py`
    * Notes:
        - "Parameters" describe inputs to the simulations themselves, such as
materials, particle types and energies, etc. "Options" describe inputs
describing pipeline behavior, such as which simulations to run, whether to save
intermediate files, etc.
        - If `pipeline.py` is run directly, the constants at the beginning of
the file are used to define the parameters and option of the run.
    * `def build_parameters(...)` / `def build_options(...)`: Takes single
named arguments representing pipeline parameters and options, respectively,
and packages them into single dictionaries.
    * `def build_options(...)`: Takes single named run options and packages
them into a single dictionary.
    * `def default_parameters()` / `def default_options()`: Create
dictionaries for parameters and options, respectively, containing their default
values.
    * `def get_file_number(filename)`: Extract the suffix number from a .mat
filename that ends in a number followed by `.mat`, e.g. `file_42.mat`. File
extension could easily be parameterized if this function could be useful
elsewhere.
    * `def find_file_number_in_list(number, file_list)`: Finds the index of a
file with a given number in an ordered list. Necessary because numbered files
won't be sorted alphabetically, so resuming execution requires a more
specialized search.
    * `def configure_and_run_lumerical(lumerical_targets, params, options,
scripts=None)`: Takes a list of charge generation files and runs lumerical
to simulate charge transport, running the specified lumerical scripts on the
simulation results
    * `def run_pipeline(params=DEFAULT_PARAMS, options=DEFAULT_OPTIONS,
scripts=None)`: Run a series of simulations in sequence. Penelope is run first,
followed by either the lightweight in-house code, or Lumerical.


### Usage Instructions

#### penelope.py

First, the pyPENELOPE root directory must be in the pythonpath, so that
pyPENELOPE can be imported into python scripts. This is the folder that
contains the folder `penelopetools`, and is probably called pyPENELOPE-0.2.10.
Export its location using its absolute path like this:

```console
z-adams@Z-ThinkPad-T450s:~$ export PYTHONPATH="${PYTHONPATH}:
/abs/path/to/pyPENELOPE-0.2.10/"
```

If it's your first time running pyPENELOPE, you'll need to create a
pypenelope.cfg file under `~/.pypenelope/pypenelope.cfg` on Linux, or
the appropriate location on other systems. The file should contain the following
lines, with the paths changed to the appropriate locations of the executables
and data files:

```ini
[Shower2010]
programname = penshower
programbasepath = /<path>/fortran/penshower

[Penepma2011]
programname = penepma
programbasepath = /<path>/fortran/penepma

[PENELOPE2011]
basenameatomicelectronshell = atomicelectronshell.txt
basenamecompositiondata = pdcompos.p08
basenamerelaxationdata = pdrelax.p11
basenamegroundstateconfigurationsdata = pdatconf.p08
pathname = /<path>/fortran/penelope/pendbase/pdfiles

[Material2011mod]
inputpath = /<path>/fortran/penelope/pendbase
programbasepath = /<path>/fortran/penelope/pendbase
programname = material

[pyPENELOPE GUI]
opendirectory = /<desired default folder>
saveresultsdirectory = /<desired default folder>
savefiguresdirectory = /<desired default folder>
simulationdirectory = /<desired default folder>
maximumdisplayedshowers = 100
```

With Penelope's path exported to the system path, the program should now be
callable from python, regardless of the location it's called from. Any script
can then call the `run_penelope()` function after importing it from penelope.py.
When run without parameters, it will simulate 10 350keV electrons incident on an
infinite CdTe substrate. Open penelope.py and look inside to see how the energy
parameters, materials, and geometry data are formatted if you want to pass them
as paramters to `run_penelope()`. Briefly, they are python dictionaries or
arrays of dictionaries that encode the values necessary to represent the various
attributes of the simulation inputs. They are detailed in comments with examples
provided around lines 70 and 130.

When penelope.py is called, it will do its work in the current working
directory (cwd). By default, this is where the script was called from.

For example:
```console
z-adams@Z-ThinkPad-T450s:~/Desktop/SU/test1/$ python ../SUpipeline/penelope.py
# OR:
z-adams@Z-ThinkPad-T450s:~/Desktop/SU/test1/$ python script_that_calls_penelope.py
```

The current working directory is `~/Desktop/SU/test1/` both in the case where
a script that imports penelope.py is in the current directory, and even in the
2nd case, since even though penelope.py lives in `~/Desktop/SU/SUpipeline/`,
it's being called from our cwd.

Note that a python script can also change the cwd using `os.chdir('path')`

#### lumerical.py

For Lumerical to be run using lumerical.py, it must be configured to be run
using the Python API. If Lumerical indicates that python integration is
available (an automation license is required), the `lumapi.py` script can then
be imported manually via the `imp` module. At the top of lumerical.py, a
conditional statement loads the script based on the operating system. Make sure
the path points to the correct location.

The arguments of `run_detector_test()` are as follows:

* `charge_data_filename`: The filepath to the .mat file containing the
generation rate matrix, to be read by Lumerical's CHARGE solver
* `working_dir`: The working directory to use when running lumerical. Files
produced by Lumerical will be saved here.
* `output_filename`: The name of the `.ldev` output file produced by Lumerical
* `material`: The name of the material to be used as the detector. This must
be one of the materials available within Lumerical, and the name must match
exactly.
* `mesh_options`: A dictionary storing the min and max mesh length scales, just
as they would be normally entered into Lumerical, in the form, e.g.
`{'min': 1e-6, 'max': 1e-5}`.
* `results`: Dictionary describing changes to the "results" field, to specify
which values you want Lumerical to compute in the results. For instance, if I
don't want to compute free and space charge, I can pass `{'free_charge': False,
'space_charge': False}` and both will be disabled in the final output. The way
they allow this to be controlled via the python API is abhorrent and I'm sorry
if it doesn't work.
* `scripts`: An optional list of lumerical scripts to be run post-simulation
* `pause`: Set to "True" if you want Lumerical to pause after the simulation.
The script will freeze and allow you to interact with Lumerical and inspect the
simulation results manually, until a key is pressed at the terminal running the
python script

#### pipeline.py

Pipeline.py uses lumerical.py and penelope.py as interfaces to pipeline the
running of the simulation process, beginning with primary particles and material
specifications and ending with charge transport and eventually optical
modulation calculations. It defines a set of arguments that describe how the
pipeline should behave, which are separated into two categories:

**Options** describe meta-propeties of the pipeline run:
* `USE_PENELOPE_FILE`: Whether or not to use an existing `pe-trajectories.dat`
file rather than producing a new one using pyPENELOPE (useful for when the
running system doesn't have PENELOPE installed)
* `RUN_LUMERICAL`: Whether or not to run the lumerical script on the results
* `WRITE_CHARGE_MAT`: Whether or not to compute a dense voxel matrix of charge
generation data, required by Lumerical
* `RUN_MANUAL_CHARGE`: Whether or not to run our in-house charge simulation
scripts
* `RUN_FROM_SIM`: Start at the nth trajectory (0 mean start at the beginning)
* `RUN_TO_SIM`: -1 to run to the last trajectory, else stop at the nth
* `PURGE_LARGE_DATA`: Whether or not to delete large intermediate simulation
files after running
* `RUN_NTH_SIM`: If not less than zero, runs only the Nth trajectory sim

**Parameters** describe the inputs of the physical simulations
* `NUM_PARTICLES`: Number of primary particles (trajectories) to simulate
* `INCLUDE_SECONDARIES`: Whether or not to simulate secondary particle
trajectories
* `BEAM_ENERGY`: Energy of primary particles
* `PARTICLE`: Which primary particle to use (1: electron, 2: photon,
3: positron)
* `PEN_MATERIALS`: Material properties for penelope simulation (see penelope.py
for details on how to create this)
* `GEOMETRY`: Geometric configuration of penelope simulation (see penelope.py)
* `LUM_MAT`: Material to use for Lumerical simulation. This will be the same
material passed to penelope in `PEN_MATERIALS`, but must use the exact name
that Lumerical uses for the material in its GUI material picker
* `LUM_MESH`: The min and max lengths allowed in the Lumerical mesh (see
section on lumerical.py)
* `LUM_RESULTS`: Configure results output (see section on lumerical.py)

At the top of pipeline.py, these options are all exposed as constants. They
will be used only if pipeline.py is run directly, rather than called by another
file.

Several functions are available that streamline the definition of the arguments:
`build_parameters()` and `build_options()` take the parameters and options as
named arguments, and pack them into a single dictionary, which can then be
passed to `run_pipeline()` when the pipeline is being run.

To make things even easier, `default_parameters()` and `default_options()`
automatically fill out dictionaries containing the default params and options.
These dicts can then be manually changed if desired. This makes it simple to,
for instance, use all the default settings, but run more particles. Rather than
entering every single parameter, one can simply do:

```python
params = default_parameters()
params['NUM_PARTICLES'] = 100
```

and the pipeline will run with all the default options apart from that single
change.

#### "batch" type scripts

The ability to run the pipeline using self-contained packages of parameters
allows it to be called programmatically. "Batch"-like scripts are what I call
scripts that generate pipeline configurations. All that is required to run
many instances of the pipeline is to write a function that produces a list of
sets of parameters/options. A simple example is as follows:

```python
def energy_sweep():
    BEAM_ENERGIES = [250e3, 300e3, 350e3, 400e3]
    configurations = []
    options = default_options()

    for E in BEAM_ENERGIES:
        params = default_parameters()
        params['BEAM_ENERGY'] = E

        configurations.append(
                {'name': "{0:d}_eV".format(int(E)),
                 'parameters': params,
                 'options': options
                })

    return configurations
```

The `run_batch()` function takes this function as an argument as well as
the option to use multiprocessing, and simply runs the pipeline as many times
as the config function specifies configurations.
