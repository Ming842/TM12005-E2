"""
This module contains functions to filter data and detect pulses in the data.
"""
import numpy as np

def filter_data(data, file_name):
    """
    Filters the data to retain only good data points.
    
    This function returns a mask that can be used to filter the data. It filters out data points when the value is below -3000 for two consecutive points.
    
    Parameters:
    data (dict): The dictionary containing the data arrays.
    file_name (str): The key to access the specific data array in the dictionary.
    
    Returns:
    np.ndarray: A boolean mask array indicating good (True) and bad (False) data points.
    """
    # Initialize a mask with all True values, indicating all data points are initially considered good
    mask = np.ones(data[file_name, 'data'].shape, dtype=bool)
    

    for i in range(12):
        # Extract the data for the current column
        data_used = data[file_name, 'data'][:, i]
        
        # Find indices where the data is below -3000
        indices = np.where(data_used < -3000)[0]
        
        # Calculate the differences between consecutive indices
        diffs = np.diff(indices, prepend=indices[0])
        
        # Identify indices where the difference is 1 (indicating consecutive bad data points)
        false_indices = indices[diffs == 1]
        
        # Update the mask to False at the identified indices for the current column
        mask[false_indices, i] = False
    
    
    # Return the mask
    return mask

def detect_pulses(data, filter_mask, file_name):
    
    """
    Detects pulses in the filtered data.
    
    This function returns a mask where true means a pulse.
    
    Parameters:
    data (dict): The dictionary containing the data arrays.
    filter_mask (np.ndarray): A boolean mask array indicating good (True) and bad (False) data points.
    file_name (str): The key to access the specific data array in the dictionary.
    
    Returns:
    np.ndarray: A boolean mask array indicating pulse (True) and no-pulse (False) data points.

    """
    # Extract the data for the given file name
    data = data[file_name, 'data']

     # Apply the filter mask to the data, replacing bad data points with NaN
    filtered_data = np.where(filter_mask, data, np.nan)

    # Initialize a mask with all False values, indicating no pulses initially
    mask = np.zeros(filtered_data.shape, dtype=bool)

    # Loop through the 12 columns of the data
    for i in range(12):
        # Extract the data for the current column
        data_used = filtered_data[:, i]

        # Find indices where the data is below -3000
        true_indices = np.where(data_used < -3000)[0]

        # Update the mask to True at the identified indices for the current column
        mask[true_indices, i] = True
    return mask

def remove_pacemaker_pulses(data: np.ndarray, filter_pulses: np.ndarray) -> np.ndarray:
    """"
    Removes pulses from the data by replacing the pulse values with the mean of the two values before the pulse."
    
    Parameters:
    data (np.ndarray): The data array.
    filer_mask (np.ndarray): A boolean mask array indicating pulse (True) and no-pulse (False) data points.

    Returns:
    np.ndarray: The data array with pulses removed.
    
    """
    data_mod = data.copy()
    index_pulses = np.where(filter_pulses)[0]
    for idx in index_pulses:
        data_mod[idx] = np.mean(data_mod [idx-2:idx-1])
    return data_mod
