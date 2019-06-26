import imp
import platform
import os
import re

#plat = platform.system()
#print(plat)
#if plat == "Linux":
lumapi = imp.load_source("lumapi", "/opt/lumerical/2019b/api/python/lumapi.py")
#elif plat == "Windows":
#    lumapi = imp.load_source("lumapi", "C:\\Program Files\\Lumerical\\2019b\\api\\python\\lumapi.py")
#elif plat == "Darwin":  # mac
#    print("I'll do this later")

# PyAPI essentially exposes the Lumerical script as python functions.
# May end up just using a lsf if this is unnecessary
def run_detector_test(charge_data, output_path=None):
    device = lumapi.DEVICE(hide=True)

    device.addchargesolver()
    device.set("min edge length", 0.1)
    device.set("max edge length", 10)
    props = device.get("spatial results")
    props = props.replace("free_charge:", "").replace("space_charge:", "")
    device.set("spatial results", props)

    device.addimportgen()
    #device.importdataset("../autoex1/test.mat")
    device.importdataset(charge_data)

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
    device.set("name", "CdTe")
    device.addmaterialproperties("CT", "CdTe (Cadmium Telluride)")
    device.select("materials::CdTe")
    device.addmaterialproperties("HT", "CdTe (Cadmium Telluride)")

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
    device.set("material", "CdTe")

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
    device.set("voltage", 0) #?
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
    device.set("voltage", 0) #?
    device.set("surface type", "solid")
    device.set("solid", "bottom_electrode")

    #device.save("../autoex1/test.ldev")
    if output_path is None:
        savepath = charge_data_filename.replace(".mat", ".ldev")
    else:
        out_file = re.split(r'[/\\]', charge_data)[-1].replace(".mat", ".ldev")
        savepath = output_path + out_file
    device.save(savepath)
    device.run()

    #try:
    #    raw_input("press any key to continue...")
    #except:
    #    pass
