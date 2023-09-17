import os.path
import pandas as pd

dataset_names = []
dataset_data = []
folder_path = 'dataset'
file_size = 0

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if os.path.isfile(os.path.join(folder_path, file)):
            df = pd.read_csv('dataset/'+ file)
            file = file[0:-7]
            dataset_names.append(file)
            dataset_data.append(df)
            file_size = file_size+1
else:
    print("the folder ", folder_path," does not exist")

dataset_dict = {}
for name, value in zip(dataset_names, dataset_data):
    dataset_dict[name] = value



