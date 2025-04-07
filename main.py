import numpy as np

import dataloader as dl
import detect_pulses as dp
import analyze_ecg as ae
import detect_setting as ds
import argparse

def main():
    """
    Main function to run the pacemaker detection algorithm.
    """
    # Load the data
    print("Loading data...")

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Pacemaker detection algorithm")
    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Directory to the folder containing the data files (absolute path)"
    )
    args = parser.parse_args()

    data_dir = args.data_dir

    #Import data
    imported_data, _ = dl.import_data(data_dir)
    data = dl.restructure_data(imported_data)
    print("Choosing data...")

    # Choose the data to be used
    data_choice, contains_atrium_fibrilation = dl.request_input(imported_data)


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
    qrs_idx, data_pt = ae.pan_tompkins(data_plot, fs)
    qrs_mask = ae.convert_to_bool(data_plot, qrs_idx)
    p_idx = ae.find_p_tops(data_plot, qrs_idx, fs)
    p_mask = ae.convert_to_bool(data_plot, p_idx)
    classified = ae.classify_pacing(p_mask, qrs_mask, data_mask, fs)
    time_pt = np.arange(0,len(data_pt),1) / fs
    ae.classify_pacemaker_settings(classified, p_mask, contains_atrium_fibrilation)

    print("Detecting settings...")

    # detect settings
    pacemaker = ds.PacingDetector(classified, p_mask, contains_atrium_fibrilation)
    setting = pacemaker.detect_setting()
    print("Settings detected:")
    print(setting) 


if __name__ == "__main__":
    main() 
