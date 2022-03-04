import os
def InpOutRead():
    # get path to current program
    pathToCode = os.getcwd()
    # ----------------------------------------------------------------------------------------------------------------------
    # please input path from current directory to inp and out files as needed
    # ----------------------------------------------------------------------------------------------------------------------
    PathToInp = pathToCode + "\\SIM FILES\\surrogate\\child_0_5\\child_0_5_sim.inp"
    PathToOut = pathToCode + "\\SIM FILES\\surrogate\\child_0_5\\child_0_5_sim.out"

    # inp will be stored as Paths[0] Out will be stored as Paths[1]

    return PathToInp, PathToOut
