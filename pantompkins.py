import numpy as np
import scipy.signal as signal
import pandas as pd


def pan_tompkins(ecg_signal: list[float], fs: int) -> tuple:
    """
    Pan-Tompkins algorithm for QRS detection.

    Parameters:
    ecg_signal (np.ndarray): The ECG signal.
    fs (int): The sampling frequency in Hz.

    Returns: 
    tuple(rppeaks, integrated_ecg): A tuple containing the R-peaks and the integrated
    rppeaks (np.ndarray): The indices of the R-peaks in the ECG signal.
    integrated_ecg (np.ndarray): The integrated ECG signal.
    """

    # Bandpass filter
    lowcut = 5.0
    highcut = 15.0
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = signal.butter(1, [low, high], btype='band')
    ecg_signal[ecg_signal < -1500] = 0
    filtered_ecg = signal.lfilter(b, a, ecg_signal)

    # Derivative filter
    derivative_ecg = np.diff(filtered_ecg)

    # Squaring
    squared_ecg = derivative_ecg ** 2

    # Moving window integration
    window_size = int(0.150 * fs)
    integrated_ecg = np.convolve(squared_ecg, np.ones(window_size)/window_size, mode='same')

    # Account for the delay introduced by the moving average
    delay = window_size // 2
    integrated_ecg = np.roll(integrated_ecg, -delay)
    integrated_ecg[integrated_ecg > 0.1*10**6] = 0
    # Find R-peaks
    threshold = np.mean(integrated_ecg) * 2
    r_peaks, _ = signal.find_peaks(integrated_ecg, height=threshold, distance=30)
    return r_peaks, integrated_ecg

def convert_to_bool(sig: np.ndarray, peak_idx: np.ndarray) -> np.ndarray:
    """
    Converts peak indexes to bools for signal
    """
    peak_bool = np.zeros(len(sig), dtype=bool)
    peak_bool[peak_idx] = True
    return peak_bool

def find_p_tops(ecg_signal: list[float], qrs_peaks: np.ndarray[bool], fs: int) -> np.ndarray:
    """
    Find P-tops in the ECG signal.

    Parameters:
    ecg_signal (np.ndarray): The ECG signal.
    qrs_peaks (np.ndarray): The indices of the QRS peaks in the ECG signal.
    fs (int): The sampling frequency in Hz.

    Returns:
    p_tops (np.ndarray): The indices of the P-tops in the ECG signal.
    """
    p_tops = []
    p_window = int(0.2 * fs)  # 200 ms window

 ## Improved P-wave Detection Code
    for qrs in qrs_peaks:
        # Set adaptive window boundaries
        start = max(0, qrs - p_window - 15)
        end = qrs  # QRS complex start position
        
        # Extract segment and find peaks
        p_segment = ecg_signal[start:end]
        
        # Enhanced peak detection with prominence filtering
        peak_indices, properties = signal.find_peaks(
            p_segment,
            prominence=10     # Minimum duration in samples
        )
        
        if peak_indices.size > 0:
            # Find most prominent peak rather than tallest
            main_peak_idx = np.argmax(properties["prominences"])
            p_top = peak_indices[main_peak_idx] + start
            p_tops.append(p_top)
        else:
            pass
    
    p_tops_boolean = np.zeros(len(ecg_signal), dtype=bool)
    p_tops_boolean[p_tops] = True
    return p_tops_boolean

def classify_pacing(p_bool: np.ndarray[bool], qrs_bool: np.ndarray[bool], 
                    pace_bool: np.ndarray[bool], fs, threshold_p_ms: float = 0.2, 
                    threshold_qrs_ms: float = 0.2):
    """
    Classifies pacing peaks into Atrial, Ventricular, or Unknown types based on given boolean arrays.

    Parameters:
    p_bool (array-like): Boolean array indicating the presence of P waves.
    qrs_bool (array-like): Boolean array indicating the presence of QRS complexes.
    pace_bool (array-like): Boolean array indicating the presence of pacing peaks.
    fs (int): Sampling frequency of the signal.
    threshold_p_ms (float, optional): Time threshold in milliseconds for P wave classification. Default is 0.2 ms.
    threshold_qrs_ms (float, optional): Time threshold in milliseconds for QRS complex classification. Default is 0.2 ms.

    Returns:
    pd.DataFrame: A DataFrame with columns ['index', 'time (s)', 'type'] indicating the index, time in seconds, and type of pacing peak.
    
    """
 
    classified_pacing = pd.DataFrame(columns=['index', 'time (s)', 'type'])
    threshold_p_samples = threshold_p_ms * fs
    threshold_qrs_samples = threshold_qrs_ms * fs
    pace_idxs = np.where(pace_bool)[0]
    for idx in pace_idxs[::-1]:
        idx = int(idx)
        time = np.round(idx / fs,2)
        if any(p_bool[idx:idx + int(threshold_p_samples)]):
            classified_pacing.loc[-1] = [idx, time, 'Atrial']
        
        elif (any(qrs_bool[idx:idx + int(threshold_qrs_samples)]) and 
              any(p_bool[idx - int(threshold_p_samples):idx])):
            classified_pacing.loc[-1] = [idx, time, 'Ventricular']
        
        else:
            classified_pacing.loc[-1] = [idx, time,'Unknown']
        classified_pacing.index = classified_pacing.index + 1
    classified_pacing = classified_pacing.sort_index()

    return classified_pacing

def classify_pacemaker_settings(classified_pacing: pd.DataFrame, pace_bool: np.ndarray[bool]):
    """
    Classifies pacemaker settings based on pacing peaks

    Parameters:
    classified_pacing (pd.DataFrame): DataFrame containing classified pacing peaks.
    pace_bool (np.ndarray): Boolean array indicating pacing peaks.

    Return: 
    pacing type (str): string indicating the type of pacemaker setting.
    """

    pace_idxs = np.where(pace_bool)[0]
    n_paces = len(pace_idxs)
    counts = classified_pacing['type'].value_counts()
    counts = counts[counts.index != 'Unknown']
    n_paces = n_paces - classified_pacing['type'].value_counts().get('Unknown', 0)
    print(counts, n_paces)
    match counts.to_dict():
        case {'Atrial': atrial_count} if atrial_count == n_paces:
            return 'Atrial Pacing'
        case {'Ventricular': ventricular_count} if ventricular_count == n_paces:
            return 'Ventricular Pacing'
        case {'Atrial': atrial_count, 'Ventricular': ventricular_count}:
            return 'Dual Pacing'


