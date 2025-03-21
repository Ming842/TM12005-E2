import os
import sys 

import scipy.io
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



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
                    imported_data[file] = array
                    imported_data_details[file] = details
    return imported_data, imported_data_details

def import_one_data(dir: str, filename) -> dict:
    """
    Import data from a directory containing .mat files
    """
    dir_path = os.path.join(dir, filename)
    details = scipy.io.whosmat(dir_path)
    array = scipy.io.loadmat(dir_path)
    imported_data = array
    imported_data_details = details
    return imported_data, imported_data_details

