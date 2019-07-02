import imp
import platform
import os

plat = platform.system()
print "Platform: {}".format(plat)
if plat == "Linux":
    lumapi = imp.load_source("lumapi", "/opt/lumerical/2019b/api/python/lumapi.py")
elif plat == "Windows":
    lumapi = imp.load_source("lumapi", "C:\\Program Files\\Lumerical\\DEVICE\\api\\python\\lumapi.py")
elif plat == "Darwin":  # mac
    print "Not implemented yet, need to find path"

# PyAPI essentially exposes the Lumerical script as python functions.
# May end up just using a lsf if this is unnecessary

def run_detector_test(charge_data_filename, output_filename=None, 
        material=None, mesh_options=None, results=None, scripts=None):
    """ Perform a test run of a (currently fixed to) CdTe volume given
    the specified charge generation volume data. For settings formats, see 
    respective locations in the code below

    arguments:
    charge_data_filename -- path to the charge generation data
    output_filename -- path to the output files, or None to use default
    material -- name (string) of material to use (must match lumerical exactly)
    mesh_options -- dict defining min and max edge lengths
    results -- dict defining which results to compute
    scripts -- list of paths to arbitrary .lsf scripts to run after simulation

    returns nothing
    """
    device = lumapi.DEVICE(hide=True)

    device.addchargesolver()

    # mesh_options = {'min': 1e-6, 'max': 1e-5}
    if mesh_options is not None:
        device.set("min edge length", mesh_options['min'])
        device.set("max edge length", mesh_options['max'])
    else:
        device.set("min edge length", 1e-6)
        device.set("max edge length", 1e-5)
    props = device.get("spatial results")

    # results = {'free_charge': False, 'space_charge': False}
    if results is not None:
        for option in results.keys():
            if results[option] == False:
                props = props.replace("{}:".format(option), "")
    else:
        props = props.replace("free_charge:", "").replace("space_charge:", "")

    device.set("spatial results", props)

    device.addimportgen()
    device.importdataset(charge_data_filename)

    w_x = device.get("x span")
    w_y = device.get("y span")
    w_z = device.get("z span")

    origin_x = w_x / 2.0
    origin_y = w_y / 2.0
    origin_z = w_z / 2.0

    electrode_thickness = 2e-6
    electrode_position = float(w_z) / 2

    sim_region_height = w_z + 2*electrode_thickness

    device.addmodelmaterial()
    if material is None:
        material = "CdTe (Cadmium Telluride)"
    device.set("name", material)
    device.addmaterialproperties("CT", material)
    device.select("materials::{}".format(material))
    device.addmaterialproperties("HT", material)

    device.addmodelmaterial()
    device.set("name", "Au")
    device.addmaterialproperties("CT", "Au (Gold) - CRC")
    device.select("materials::Au")
    device.addmaterialproperties("HT", "Au (Gold) - CRC")

    device.select("simulation region")
    device.set("dimension", "3D")
    device.set("x span", w_x)
    device.set("y span", w_y)
    device.set("z span", sim_region_height)
    device.set("x", origin_x)
    device.set("y", origin_y)
    device.set("z", origin_z)

    device.setview("extent")

    device.addchargemonitor()
    device.set("save data", 1)
    device.set("filename", "charge.mat")

    device.addrect()
    device.set("name", "interaction_vol")
    device.set("x span", w_x)
    device.set("y span", w_y)
    device.set("z span", w_z)
    device.set("x", origin_x)
    device.set("y", origin_y)
    device.set("z", origin_z)
    device.set("material", material)

    device.addrect()
    device.set("name", "top_electrode")
    device.set("x span", w_x)
    device.set("y span", w_y)
    device.set("z span", w_z)
    device.set("x", origin_x)
    device.set("y", origin_y)
    device.set("z", origin_z)
    device.set("z min", origin_z + electrode_position)
    device.set("z max", origin_z + electrode_position + electrode_thickness)
    device.set("material", "Au")

    device.addelectricalcontact()
    device.set("name", "top_electrode")
    device.set("bc mode", "steady state")
    device.set("sweep type", "single")
    device.set("voltage", 0)
    device.set("surface type", "solid")
    device.set("solid", "top_electrode")

    device.addrect()
    device.set("name", "bottom_electrode")
    device.set("x span", w_x)
    device.set("y span", w_y)
    device.set("x", origin_x)
    device.set("y", origin_y)
    device.set("z min", origin_z - electrode_position - electrode_thickness)
    device.set("z max", origin_z - electrode_position)
    device.set("material", "Au")

    device.addelectricalcontact()
    device.set("name", "bottom_electrode")
    device.set("bc mode", "steady state")
    device.set("sweep type", "single")
    device.set("voltage", 0)
    device.set("surface type", "solid")
    device.set("solid", "bottom_electrode")

    if output_filename is None:
        savepath = charge_data_filename.replace(".mat", ".ldev")
    else:
        savepath = output_filename
    device.save(savepath)
    device.run()

    # evaluate arbitrary scripts
    if scripts is not None:
        for script in scripts:
            device.feval(script)

if __name__ == '__main__':
    print "current location: {}".format(os.getcwd())
    datafile = raw_input("Where is the charge data .mat?: ")
    run_detector_test(datafile)
