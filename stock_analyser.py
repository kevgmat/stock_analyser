import os.path
import pandas as pd

dataset = []
folder_path = 'dataset'
file_size = 0

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)):
            file = file[0:-7]
            dataset.append(file)
            file_size = file_size+1
else:
    print("the folder ", folder_path," does not exist")

