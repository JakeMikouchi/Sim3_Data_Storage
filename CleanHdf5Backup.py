import h5py
import numpy as np
# ----------------------------------------------------------------------------------------------------------------------
# run script after all data has been stored
# ----------------------------------------------------------------------------------------------------------------------

# open hdf5 file and access data
Hdf5_Name = "Sim3data.hdf5"
f1 = h5py.File(Hdf5_Name, "a")
f2 = f1.get("data")

repeatedData = []
AllFA = []
DeletedData = 0

# stores names for all keys in "data" group of Hdf5
keys = [key for key in f2]
keys = sorted([int(i) for i in keys])

# iterates through all keys

print("comparing data")
for Current in keys:
    # pulls out Fuel assembly from key that is being compared to others
    currentGroup = f2.get(f"{Current}")
    currentFA = np.array(currentGroup.get(f"Fuel_Assembly"))
    # variable for while loop
    loop = int(keys.index(Current))
    while loop < len(keys):
        # pulls out all fuel assemblies to compare
        compareGroup = f2.get(f"{loop}")
        compareFA = np.array(compareGroup.get(f"Fuel_Assembly"))
        if np.array_equal(compareFA, currentFA) == True and keys[loop] != Current:  # and Current != keys[loop]:
            # stores the group names for repeated data
            repeatedData.append([Current, keys[loop]])

        loop += 1

print("organizing data")
# gets rid of any repeats in repeated data
repeatedData = list(set([i[1] for i in repeatedData]))
# deletes data
if not repeatedData:
    print("There is no repeating data")
else:
    for nest in repeatedData:
        if nest > 0:
            del f2[f"{nest}"]
            DeletedData += 1
    # tells user how many keys were deleted
    print(f"deleted {DeletedData} group(s)")

# gets remaining keys
print("reorganizing remaining data")
keys = sorted([int(i) for i in [key for key in f2]])
# iterates through keys
for key in keys:
    currentkey = keys.index(key)
    if key != currentkey:
        # sets keys to their index value
        f2[f"{currentkey}"] = f2[f"{key}"]
        del f2[f"{key}"]
    # a list of keys like [1,5,10,59] will become [0,1,2,3]
print("complete")
