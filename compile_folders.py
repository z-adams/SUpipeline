import os
import shutil
import re


def collect_data():
    """Call this function to collect and sort data

    In a directory structure like this:
    results/
    |- CdTe_350keV     This function will create a directory at the level of
    |  |- results/     the data folders ("CdTe_...", etc) called "compiled"
    |      |- n.txt    and copy all the "n.txt" data files into the new folder, 
    |- CdTe_400keV     naming each after its original location and separating
    |  |- ...          them by material
    """
    DIR_NAME = "compiled"
    dirlist = os.listdir('.')

    os.mkdir(DIR_NAME)

    for item in dirlist:
        if not os.path.isdir(item):
            continue
        mat = re.search(r'([a-zA-Z0-9]+(?=_))', item)
        if not os.path.isdir("{0}/{1}".format(DIR_NAME, mat.group(0))):
            os.mkdir("{0}/{1}".format(DIR_NAME, mat.group(0)))
        shutil.copyfile("{0}/results/n.txt".format(item),
                "{0}/{1}/{2}.txt".format(DIR_NAME, mat.group(0), item))

if __name__ == "__main__":
    collect_data()
