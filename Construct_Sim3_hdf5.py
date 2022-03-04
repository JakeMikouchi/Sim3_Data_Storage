from InpOutRead import *
import h5py
import numpy as np

# ---------------------------------------------------------------------------------------------------------------------
Hdf5_Name = "Sim3data.hdf5"
# any name changes to Hdf5_Name must also be done in CleanHdf5.py line 9
# ---------------------------------------------------------------------------------------------------------------------

# open / create files
f1 = h5py.File(Hdf5_Name, "a")
f2 = f1.require_group("data")
# find path for input and output from path given by user
Paths = InpOutRead()

# creates an array containing the fuel assembly for storage
FAdata = []
fSimin = open(Paths[0])
lines = fSimin.readlines()
FAsearch = "FUE.TYP"
FAstart = ', '
FAend = '/'
for line in lines:
    if FAsearch in line:
        LineData = (line.split(FAstart)[1].split(FAend)[0])
        FAdata.append(LineData.split(" "))

# if general info group does not exist a group will be made
if 'General_Info' not in f1:
    # create general info group
    fgen = f1.create_group("General_Info")
    # find base fuel Assembly Layout that will be compared to others

    # create general Fuel Assembly

    # General Info Folder

    # create array of string with info
    GenInfostrList = ['Boron Data', 'efpd Data', 'Max Pin Data', 'Max Assembly Data', 'Max Fuel Average Temp (K)']
    # convert to ascii
    asciiGenInfoList = [n.encode("ascii", "ignore") for n in GenInfostrList]
    # create dataset with gen info

    # fuel assembly info:
    # FA dimensions are now stored as tuple, can be called with FAdim[0] or FAdim[1]
    FAGenInfo = []
    FAGenLineInfo = []
    # checks Fuel Assembly of a data set and stores the positions of 1s and 0s
    for row in FAdata:
        for digit in row:
            if int(digit) == 1:
                FAGenLineInfo.append(1)
            elif int(digit) == 0:
                FAGenLineInfo.append(0)
            else:
                FAGenLineInfo.append(9)
        FAGenInfo.append(FAGenLineInfo)
        FAGenLineInfo = []

    CoreCondList = ['Percent Thermal Power', 'Percent Core Flow',
                    'Operating Pressure (psia)', 'Core Inlet Temp (F)', 'Coolant Average Temp (K)']
    asciiCoreCondList = [n.encode("ascii", "ignore") for n in CoreCondList]

    fSimout = open(Paths[1])
    fSimin = open(Paths[0])

    #------------------------------------------------------------------------------------------------------------------
    # Coolant Average temp data (in kelvin)

    lines = fSimout.readlines()
    CALineNum = 0
    CAdata = []
    CAsearch = "Coolant Average"

    for line in lines:
        # add 1 to CALineNum for each line read
        CALineNum = CALineNum + 1
        # if keyword "Coolant Average" is found
        if CAsearch in line:
            # find lines with coolant data
            CALine = lines[CALineNum - 1]
            # extract data from line
            CATemp = CALine[36:43]

            CAdata.append(float(CATemp))

    # ----------------------------------------------------------------------------------------------------------------------

    # Fuel Average temp data (in kelvin)
    FuelAvLineNum = 0
    FuelAvdata = []
    FuelAvsearch = "Fuel    Average"

    for line in lines:
        # add 1 to CALineNum for each line read
        FuelAvLineNum = FuelAvLineNum + 1
        # if keyword "Fuel    Average" is found
        if FuelAvsearch in line:
            # find lines with FUEL data
            FuelAvLine = lines[FuelAvLineNum - 1]
            # extract data from line
            FuelAvTemp = FuelAvLine[36:43]

            FuelAvdata.append(float(FuelAvTemp))
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # Cor.Ope data
    CorConLineNum = 0
    CorConsearch = "COR.OPE"
    # read input file
    CorConLines = fSimin.readlines()

    for line in CorConLines:
        # add 1 to CorConLineNum for each line read
        CorConLineNum = CorConLineNum + 1
        # if keyword "'COR.OPE'" is found
        if CorConsearch in line:
            # find lines with data
            CorConLine = CorConLines[CorConLineNum - 1]
            # extract data from line
            CorConTotalData = CorConLine[10:30]
            CorConSplit = CorConTotalData.split(", ")
            # all data can be put in list using split since all data is on one line
            CorCons = [float(item) for item in CorConSplit]
            # find line for core inlet temp which is next line down from cor.ope
            CorTinLine = CorConLines[CorConLineNum]
            # get cor.tin data
            CorTinData = CorTinLine[10:15]
            # add to core conditions list
            CorCons.append(float(CorTinData))
            # add Coolant average temp (found earlier in code) to core conditions
            CorCons.append(max(CAdata))

    fSimout.close()
    fSimin.close()


    # add data to general info group
    fgen.create_dataset("Fuel_Assembly_General_Info", data=FAGenInfo)
    fgen.create_dataset('Object_Info', (len(asciiGenInfoList), 1), 'S50', asciiGenInfoList)
    fgenCC = fgen.create_group("Core_Conditions")
    fgenCC.create_dataset("Core_Conditions_info", (len(asciiCoreCondList), 1), 'S50', asciiCoreCondList)
    fgenCC.create_dataset("Core_Conditions_data", data=CorCons)
# Checks to makes sure the incoming Fuel Assembly is within acceptable parameters
def FuelAssemblyCheck(FAdata, Hdf5_Name):
    # Load existing hdf5  file
    dataset = h5py.File(Hdf5_Name, "r")
    # set General Info dataset to variable
    GenInfo = dataset.get("General_Info")
    # Pull out General fuel Assembly
    GenFA = np.array(GenInfo.get("Fuel_Assembly_General_Info"))

    #----------------------------------------------------------------------------------------------------------------
    # because of how hdf5 stores data, GenFA is converted to GenFAforC for easier comparison
    m = len(GenFA)
    w = 0
    GenFAforC = []
    while w < m:
        linearray = []
        y = 0
        x = len(GenFA[w])
        while y < x:
            linearray.append(GenFA[w][y])
            y += 1
        GenFAforC.append(linearray)
        w += 1
    #----------------------------------------------------------------------------------------------------------------

    # convert FAdata to list of ints rather than list of strings
    FAcheck = []
    i = 1
    while i <= len(FAdata):
        FAcheck.append(list(map(int, FAdata[i - 1])))
        i += 1

    # Converts all ints greater than 1 into 9s to be compared to GenFA
    FAInfo = []
    FALineInfo = []
    # checks Fuel Assembly of a data set and stores the positions of 1s and 0s
    for row in FAcheck:
        for digit in row:
            if int(digit) == 1:
                FALineInfo.append(1)
            elif int(digit) == 0:
                FALineInfo.append(0)
            else:
                FALineInfo.append(9)
        FAInfo.append(FALineInfo)
        FALineInfo = []

    # compares FAInfo to GenFA if they are the same TorF will equal 1 if not then TorF will equal 0
    if len(FAInfo) == len(GenFAforC):
        z = (FAInfo == GenFAforC)
        if z == True:
            TorF = 1
        else:
            TorF = 0
    else:
        TorF = 0

    dataset.close()
    return TorF
# checks if incoming core conditions are the same as in general core conditions
def CoreConditionsCheck(CCdata, Hdf5_Name):
    # Load existing hdf5  file
    dataset = h5py.File(Hdf5_Name, "r")
    # set General Info dataset to variable
    GenInfo = dataset.get("General_Info")
    # set core conditions group = GenCC
    GenCC = GenInfo.get("Core_Conditions")
    # Pull out General Core Conditions
    GenCCD = np.array(GenCC.get("Core_Conditions_data"))
    # compare the two Core Conditions
    Compare = np.array_equal(GenCCD,CCdata)
    # if the core conditions are equal then output a 1, if they do not match then output a 0
    if Compare == True:
        TorF = 1
    else:
        TorF = 0

    dataset.close()
    return TorF
# retrieves data from outpu and input files
def DataAnalysis(Output, Input):
    fSimout = open(Output)
    fSimin = open(Input)
    # -----------------------------------------------------------------------------------------------------------------------
    # read .out file
    lines = fSimout.readlines()
    efpdData = []
    efpdLineNum = 0
    efpdsearch = "EFPD"
    # go through .sum file iteratively
    for line in lines:
        # add 1 to LineNum for each line read
        efpdLineNum = efpdLineNum + 1
        # if keyword "" is found
        if efpdsearch in line:
            # add to x matrix for each dataset of boron found
            # find lines with boron data
            BoronLine = lines[efpdLineNum - 1]
            # extract boron data from line
            Boron = BoronLine[98:105]
            efpdData.append(float(Boron))

    # -----------------------------------------------------------------------------------------------------------------------
    # read .out file
    BoronData = []
    BLineNum = 0
    Bsearch = "Boron Conc. . . . . . . . . . BOR"
    # go through .sum file iteratively
    for line in lines:
        # add 1 to LineNum for each line read
        BLineNum = BLineNum + 1
        # if keyword "" is found
        if Bsearch in line:
            # add to x matrix for each dataset of boron found
            # find lines with boron data
            BoronLine = lines[BLineNum - 1]
            # extract boron data from line
            Boron = BoronLine[36:42]
            BoronData.append(float(Boron))
    # ----------------------------------------------------------------------------------------------------------------------

    # Peaking factor Max Pin
    # create an x variable for plot
    MPLineNum = 0
    MPdata = []
    MPsearch = "Batch Summary"

    for line in lines:
        # add 1 to DSLLineNum for each line read
        MPLineNum = MPLineNum + 1
        # if keyword "Max. Node-Averaged" is found
        if MPsearch in line:
            # find lines with Peaking factor data data
            MPLine = lines[MPLineNum + 6]
            # extract P data from line
            PeakingFactorMaxPin = MPLine[70:75]
            MPdata.append(float(PeakingFactorMaxPin))

    # ----------------------------------------------------------------------------------------------------------------------


    # Peaking factor Max Pin
    MALineNum = 0
    MAdata = []
    MAsearch = "Batch Summary"

    for line in lines:
        # add 1 to DSLLineNum for each line read
        MALineNum = MALineNum + 1
        # if keyword "Max. Node-Averaged" is found
        if MAsearch in line:
            # find lines with Peaking factor data data
            MALine = lines[MALineNum + 6]
            # extract P data from line
            PeakingFactorMaxAssem = MALine[88:93]
            MAdata.append(float(PeakingFactorMaxAssem))

    # ----------------------------------------------------------------------------------------------------------------------

    # Coolant Average temp data (in kelvin)
    CALineNum = 0
    CAdata = []
    CAsearch = "Coolant Average"

    for line in lines:
        # add 1 to CALineNum for each line read
        CALineNum = CALineNum + 1
        # if keyword "Coolant Average" is found
        if CAsearch in line:
            # find lines with coolant data
            CALine = lines[CALineNum-1]
            # extract data from line
            CATemp = CALine[36:43]

            CAdata.append(float(CATemp))

    # ----------------------------------------------------------------------------------------------------------------------

    # Fuel Average temp data (in kelvin)
    FuelAvLineNum = 0
    FuelAvdata = []
    FuelAvsearch = "Fuel    Average"

    for line in lines:
        # add 1 to CALineNum for each line read
        FuelAvLineNum = FuelAvLineNum + 1
        # if keyword "Fuel    Average" is found
        if FuelAvsearch in line:
            # find lines with FUEL data
            FuelAvLine = lines[FuelAvLineNum - 1]
            # extract data from line
            FuelAvTemp = FuelAvLine[36:43]

            FuelAvdata.append(float(FuelAvTemp))
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # Cor.Ope data
    CorConLineNum = 0
    CorConsearch = "COR.OPE"
    # read input file
    CorConLines = fSimin.readlines()

    for line in CorConLines:
        # add 1 to CorConLineNum for each line read
        CorConLineNum = CorConLineNum + 1
        # if keyword "'COR.OPE'" is found
        if CorConsearch in line:
            # find lines with data
            CorConLine = CorConLines[CorConLineNum - 1]
            # extract data from line
            CorConTotalData = CorConLine[10:30]
            CorConSplit = CorConTotalData.split(", ")
            # all data can be put in list using split since all data is on one line
            CorCons = [float(item) for item in CorConSplit]
            # find line for core inlet temp which is next line down from cor.ope
            CorTinLine = CorConLines[CorConLineNum]
            # get cor.tin data
            CorTinData = CorTinLine[10:15]
            # add to core conditions list
            CorCons.append(float(CorTinData))
            # add Coolant average temp (found earlier in code) to core conditions
            CorCons.append(max(CAdata))



    # -----------------------------------------------------------------------------------------------------------------------


    fSimout.close()
    fSimin.close()
    return [max(BoronData), max(efpdData), max(MPdata), max(MAdata), max(FuelAvdata)], CorCons


# count number of groups in "data" folder
CurrentGroup = len(f2.keys())

# checks if Fuel Assembly matches with general Fuel Assembly
# if FuelAssemblyCheck == 1 then a new set of data will be stored
# if = 0 then no data is stored

if FuelAssemblyCheck(FAdata, Hdf5_Name) == 1:

    # extracts all needed info from files
    Condense = DataAnalysis(Paths[1], Paths[0])

    if CoreConditionsCheck(Condense[1], Hdf5_Name) == 1:
        # creates group for data that is being stored with name as next number in line
        f3 = f2.create_group(f"{CurrentGroup}")
        print(f"Created group {CurrentGroup}. There are Currently {CurrentGroup+1} group(s) stored.")
        # creates an array containing the fuel assembly for storage

        # extracts all needed info from files
        Condense = DataAnalysis(Paths[1], Paths[0])

        # uploads data into hdf5 file
        f3.create_dataset("Objective_Goals", data=Condense[0])
        f3.create_dataset("Core_Conditions", data=Condense[1])
        f3.create_dataset(f"Fuel_Assembly", data=FAdata)

    else:
        print("The Core Conditions do not match")

else:
    print("Fuel Assembly given does not match General Fuel Assembly")
    print("Fuel Assembly dimensions may not be correct or the positions of 1s and 0s do"
          " not match General Fuel Assembly")

# close files
f1.close()


