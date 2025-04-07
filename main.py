import numpy as np


import dataloader as dl
import detect_pulses as dp
import pantompkins as pt
import detect_setting as ds

print("Loading data...")

#import data
imported_data, imported_data_details = dl.import_data(r'C:\Users\jelle\OneDrive - Delft University of Technology\TM12005 Advanced Signal Processing\opdracht 2\data')
data = dl.restructure_data(imported_data)

print("choosing data")

#choose the data to be used
data_test = data['005_Pimpel.mat', 'data']
mask_filter = dp.filter_data(data,"005_Pimpel.mat")
idx_pulses = dp.detect_pulses(data, mask_filter, "005_Pimpel.mat")
data_plot = data_test[:,1]
data_raw = data_test[:,1]
data_mask = idx_pulses[:,1]
fs = data['005_Pimpel.mat', 'header', 'sample_rate']

print("performing calculations")

#perform all functions
data_plot = dp.remove_pacemaker_pulses(data_plot, data_mask)
qrs_idx, data_pt = pt.pan_tompkins(data_plot, fs)
qrs_mask = pt.convert_to_bool(data_plot, qrs_idx)
p_idx = pt.find_p_tops(data_plot, qrs_idx, fs)
p_mask = pt.convert_to_bool(data_plot, p_idx)
classified = pt.classify_pacing(p_mask, qrs_mask, data_mask, fs)
time_pt = np.arange(0,len(data_pt),1) / fs
pt.classify_pacemaker_settings(classified, p_mask)

print("detecting settings")

# detect settings
pacemaker = ds.PacingDetector(classified, p_mask)
setting = pacemaker.detect_setting()

print(setting)
