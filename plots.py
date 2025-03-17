import os
import sys 

import scipy.io
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

dir = 'data'


def import_data(dir: str) -> dict:
    """
    Import data from a directory containing .mat files
    """
    imported_data = {}
    imported_data_details = {}
    filenames = os.listdir(dir)
    for file in filenames:
        if file.endswith('.mat'):
                    dir_path = os.path.join(dir, file)
                    details = scipy.io.whosmat(dir_path)
                    array = scipy.io.loadmat(dir_path)
                    imported_data[file] = array['ecg']
                    imported_data_details[file] = details
    return imported_data, imported_data_details

# def plot_data(data):
#     """
#     Plot data from data
#     """
#     plt.figure()
#     plt.plot(data)
#     plt.title('data')
#     plt.show()

data, info = import_data(dir)

# Parse metadata
