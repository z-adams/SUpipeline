# In the future, may want to have config files to generalize 
# http://pypenelope.sourceforge.net/code/penelopetools/api/input/penelope/description.html

from penelopetools import *
desc = Description()
desc.title('myTitle')

### Microscope ("source")
src = Source()
# set particle type
# see "interactionforcings.Collisions" in API documentation

# set incident energy
src.beam_energy = 20000.0

# set beam diameter

# set tilt

# est rotation

# set beam position (x, y)

### Geometry
# Select geometry (substrate)

# Create and select material
Cd = Element('Cd')
Te = Element('Te')

elems = Elements()
# elems.add(symbol, fraction=1.0)
elems.add_element(Cd)
elems.add_element(Te)

mat = Material(name=None, filename=None, elements=None, simulation_paramters=None)
mat.elements = elems

mats = Materials()
mats.add(mat, userid=None)
### Simulation
# penelopetools.api.input.penelope.materials.SimulationParamters
sim = SimulationParameters()
# absorption of e-, e+, phot
sim.absorption_energy_electron(50)
sim.absorption_energy_photon(50)
sim.absorption_energy_positron(50)

# elastic scattering parameters C1, C2
sim.elastic_scattering_paramters_c1(0.1)
sim.elastic_scattering_paramters_c2(0.1)

# cutoff energy loss
sim.cutoff_energyloss_inelasticcollisions(50)
sim.cutoff_energyloss_bremsstrahlungemission(50)

# can get xml/in config files
sim.to_inputfile()
sim.to_xml()

### Trajectories

# number of electrons

# track secondary particles?
