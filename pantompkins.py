import numpy as np
import scipy.signal as signal

def pan_tompkins(ecg_signal, fs) -> tuple:
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

def find_p_tops(ecg_signal, qrs_peaks, fs) -> np.array:
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
        start = max(0, qrs - p_window)
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
