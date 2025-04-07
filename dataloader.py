import os
import sys 

import scipy.io
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



def import_data(dir) -> dict:
    """
    Import data from a directory containing .mat files
    """
    dir = os.path.abspath(dir)
    imported_data = {}
    imported_data_details = {}
    filenames = os.listdir(dir)
    for file in filenames:
        if file.endswith('.mat'):
                    dir_path = os.path.join(dir, file)
                    details = scipy.io.whosmat(dir_path)
                    array = scipy.io.loadmat(dir_path)
                    imported_data[file] = array
                    imported_data_details[file] = details
    return imported_data, imported_data_details

def restructure_data(data: dict) -> dict:
    """
    Restructure data from a dictionary to a pandas DataFrame
    """
    restructured_data = {}
    for key in data.keys():
        signals = data[key]['ecg']['sig'][0][0]
        sample_rate = data[key]['ecg']['header'][0][0]['Sampling_Rate'][0][0][0][0]
        sample_size = data[key]['ecg']['header'][0][0]['Sample_Size_ECG'][0][0][0][0]
        restructured_data[key,'data'] = signals
        restructured_data[key,'header', 'sample_rate'] = sample_rate
        restructured_data[key,'header', 'sample_size'] =  sample_size
    return restructured_data

def request_input(imported_data):
    filenames = list(imported_data.keys())
    filenames_printable = ', '.join(filenames[:-1]) + ' and ' + filenames[-1] if len(filenames) > 1 else filenames[0]

    while True:
        choice = input(f"Choose the data to be used, available filenames \n {filenames_printable}: ").strip()
        if choice in filenames:
            data_choice = choice
            print(f"Data chosen: {data_choice}")
            break
        else:
            print("Invalid choice. Please choose a valid data file.")
    # Request user input to determine if the signal contains atrium fibrilation
    while True:
        user_input = input("Does the signal contain atrium fibrilation? (true/false): ").strip().lower()
        if user_input in ['true', 'false']:
            contains_atrium_fibrilation = user_input == 'true'
            print(f"Atrium fibrilation: {contains_atrium_fibrilation}")
            break
        else:
            print("Invalid input. Please enter 'true' or 'false'.")
    return data_choice, contains_atrium_fibrilation

if __name__ == '__main__':
    dir = r'E:\OneDrive\School\Technical Medicine\TM Jaar 1\TM12004 - Advanced Signal Processing\data'
    data, info = import_data(dir)
    print(data)
    print(info)