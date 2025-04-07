import numpy as np


import dataloader as dl
import detect_pulses as dp
import pantompkins as pt
import detect_setting as ds

def main():
    """
    Main function to run the pacemaker detection algorithm.
    """
    # Load the data
    print("Loading data...")

    #Import data
    imported_data, _ = dl.import_data(r'c:\Users\mdcalje\OneDrive\School\Technical Medicine\TM Jaar 1\TM12004 - Advanced Signal Processing\data')
    data = dl.restructure_data(imported_data)
    print("Choosing data...")

    # Choose the data to be used
    data_choice, contains_atrium_flutter = request_input(imported_data)


    data_test = data[data_choice, 'data']
    mask_filter = dp.filter_data(data, data_choice)
    idx_pulses = dp.detect_pulses(data, mask_filter, data_choice)
    data_plot = data_test[:,1]
    data_raw = data_test[:,1]
    data_mask = idx_pulses[:,1]
    fs = data[data_choice, 'header', 'sample_rate']

    print(f"Performing calculations for {data_choice}...")

    # Perform all calculations
    data_plot = dp.remove_pacemaker_pulses(data_plot, data_mask)
    qrs_idx, data_pt = pt.pan_tompkins(data_plot, fs)
    qrs_mask = pt.convert_to_bool(data_plot, qrs_idx)
    p_idx = pt.find_p_tops(data_plot, qrs_idx, fs)
    p_mask = pt.convert_to_bool(data_plot, p_idx)
    classified = pt.classify_pacing(p_mask, qrs_mask, data_mask, fs)
    time_pt = np.arange(0,len(data_pt),1) / fs
    pt.classify_pacemaker_settings(classified, p_mask)

    print("Detecting settings...")

    # detect settings
    pacemaker = ds.PacingDetector(classified, p_mask, contains_atrium_flutter)
    setting = pacemaker.detect_setting()
    print("Settings detected:")
    print(setting) 

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
    # Request user input to determine if the signal contains atrium flutter
    while True:
        user_input = input("Does the signal contain atrium flutter? (true/false): ").strip().lower()
        if user_input in ['true', 'false']:
            contains_atrium_flutter = user_input == 'true'
            print(f"Atrium flutter: {contains_atrium_flutter}")
            break
        else:
            print("Invalid input. Please enter 'true' or 'false'.")
    return data_choice, contains_atrium_flutter

if __name__ == "__main__":
    main() 
