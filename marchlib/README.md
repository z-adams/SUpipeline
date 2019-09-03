# marchlib - barebones raymarcher for solid state optical simulation
#### Zander Adams

## How to make it work:

The raymarcher works as a standalone library, but was designed to be called as
a subprocesses by a python script. `pymarch.c` provides a `main()` function
which allows the library to run automatically when compiled. It is set up to
communicate with a parent process over standard input and output.

`pymarch.py` is a script that defines the `run_raymarcher()` function for easy
calling of the C executable. Follow these steps to get the library running:

1. Clone this repository into a folder near your particle trajectory data
(from pyPENELOPE)

2. Write a script that uses the `traj_parser` and `charge_density` modules to
generate a list of charge density objects of `class Cloud`

3. Define a step resolution (units of cm) and projection (currently not
implemented) **Note: resolutions < 1e-5cm may take a long time to run**

4. Call the raymarcher: 

```python
data = run_raymarcher(volumes, resolution, projection)
```
The raymarcher will return a 2D numpy array containing a projected volume
integration of the charge data. Do math on it or plot it with matplotlib's
`imshow`, for example.

## Details

Raymarching is effectively a method of numerical volume integration, typically
used for computer graphics. It projects a ray into the scene (usually
simulating a light ray) and, rather than simply immediately calculating its
points of intersection with the geometry, it steps ("marches") along the ray at
discrete points and samples the volume. "Signed Distance Functions" allow the
function to compute the nearest surface as an upper bound step size, or
calculate whether or not a point is inside a volume.

The end result is similar to Riemann sums, where at each point in the grid
implicitly described by the fixed-step integration, the value measured is
assumed to be homogenous across the volume element.

This library can perform arbitrary calculations at each point, since the
function used to sample the volume is specified by the user, as is the format
of the output.

`pymarch.c` provides a C wrapper for the library to be called as a subprocess,
using standard input and output to pass binary data via pipe. `pymarch.py` is
a python wrapper for the `pymarch` executable, and provides an easy to use
interface for the raymarcher.

Upon execution, `pymarch.py` launches the `pymarch` executable as a subprocess.
It begins transferring the charge volume data, received as an argument and
packed as binary data using the `struct` module, to the subprocess via pipe.
The python script then blocks itself on a read from the subprocess's `stdout`
and waits. When the subprocess finishes its computation, it pipes the dimensions
of the data array out via `stdout`, followed by the data itself, which is
subsequently received and returned to the caller.
