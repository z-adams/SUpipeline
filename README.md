# pyPENELOPE -> Lumerical simulation pipeline
#### Zander Adams

## How to make it work:

Prerequisites: pyPENELOPE's home directory must be in your PYTHONPATH, and
there must be Automation and Charge licenses available for Lumerical.

The only file you should have to directly interact with is pipeline.py, unless
you want to use one of the sub components manually. 

1. Create a new directory for the input and output. I put it just outside the
SUpipeline directory, but it can go anywhere. 

2. If you have any .lsf scripts to run on the Lumerical simulation results, or
a `pe-trajectories.dat` file from PENELOPE that you want to use instead of the
pipeline simulating its own trajectories, place them inside your new directory.

3. Run pipeline.py from your new folder (see below)

For example, I clone SUpipeline into a directory and create a new folder with
my inputs (for the sake of example let's say I have both an .lsf script and an
existing batch of PENELOPE data), yielding the following situation:

```
Parent_dir/
 |-- SUpipeline/
 |    |-- pipeline.py
 |    +-- <other stuff>
 |-- myFolder/
 |    |-- get_3D_n_matrix.lsf
 |    +-- pe-trajectories.dat
```

I can then cd into my working directory (myFolder) and run pipeline like this:

```console
zander@T450s:~/.../Parent_dir$ cd myFolder
zander@T450s:~/.../Parent_dir/myFolder$ python ../SUpipeline/pipeline.py
```

and pipeline.py will do its work in our new folder.

After running, the directory will look like this:
```
Parent_dir/
 |-- SUpipeline/
 |    |-- pipeline.py, etc
 |
 |-- myFolder/
 |    |-- pyPENELOPE/
 |    |    |-- pe-trajectories.dat
 |    |    +-- other files, if PENELOPE actually ran (not in this case)
 |    |
 |    |-- results/
 |    |    |-- generation_0/
 |    |    |    |-- x_, y_, z_rect.mat
 |    |    |    +-- ref_rect.mat, abs_rect.mat
 |    |    |-- generation_1/
 |    |   ... 
 |    |    |-- generation_n/
 |    |   
 |    +-- scripts/
 |         |-- get_3D_n_matrix.lsf

```


## Details

#### Arguments

Right now there is only one command line argument, used to set the logging
level. The options are `WARNING`, `INFO`, and `DEBUG`, in order of increasing
verbosity. The argument is used when running the pipeline, like this:

```console
zander@T450s:~/.../myFolder$ python ../SUpipeline/pipeline.py --log=INFO
```

At the beginning of pipeline.py, there are a series of constants and parameters
that should cover any configuration options necessary. They are:

#### Constants

* `USE_PENELOPE_FILE`: If true, the program will use an existing data file
instead of using pyPENELOPE to run a new simulation.

* `LUM_SIM_LIMIT`: The maximum number of lumerical simulations to run, or -1
to perform a run for all trajectories. This is useful if you are using an
existing data file (see above) that has a large number of trajectories but
don't want to simulate the charge transport for every single one.

* `PURGE_LARGE_DATA`: Removes intermediate files (charge generation and 
lumerical simulation output) after the simulation has completed and optical 
modulation has been determined. Those files often add up to be many Megabytes
which would result in an enormous amount of data for very large simulation
batches

* `RUN_NTH_SIM`: Used to force only a specific simulation to run in lumerical.
If you had, say, 100 PENELOPE trajectories and their associated charge
generation matrices, and only wanted to run \#37, you would set this variable to
37\. Set it to -1 to simulate all trajectories.

#### Parameters
* `NUM_PARTICLES`: The number of primary particles (i.e. showers) to simulate
in pyPENELOPE

* `BEAM_ENERGY`: The kinetic energy of each primary

* `PEN_MATERIALS`: The materials to use in the PENELOPE simulation (see
[materials](#materials)

* `GEOMETRY`: The geometry to use for the PENELOPE simulation (also see below)

* `LUM_MAT`: The material to use for the Lumerical simulation (the same
as used in PENELOPE; must have the exact same name as it does in Lumerical.

* `LUM_RESULTS`: Dict defining which results to omit from the simulatoin. See
lumerical.py for more information.

#### Don't touch

* `DATA_FILE_PATH`: the filepath where the electron shower trajectory data
file will be found. Shouldn't need to change.

* `SCRIPTS`: Contains a list of scripts to run on the Lumerical simulation
data, but the array is filled in automatically with whatever `.lsf` script
files are placed in the working directory, so you shouldn't modify it.

## Materials

Materials and geometry are sort of a complicated thing to expose in a simple
way, so instead I exposed them in a convoluted and user unfriendly way. Just
kidding, it's just a little annoying.

The PENELOPE materials are created with a dict that has the following keys:

* `'name'`: The name of the material (a string). Used to specify what material
is used by the geometry, so this is the material's ID.

* `'density'`: The density of the material (a number)

* `'elements'`: A list of tuples containing an element (i.e. its chemical
symbol [case sensitive]) and its mass fraction.

The geometries are constructed in more or less similar ways.

Pipeline.py explicitly passes the default settings for these properties as an
example; if you want to understand it better than that have a look in
penelope.py for more explanation and to see how the code actually uses those
values.
