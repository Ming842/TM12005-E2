# TM12005-E2: Advanced Signal Processing - Python Pacemaking

This repository contains Python scripts related to the Advanced Signal Processing course (TM12004). The scripts are designed to analyze and process signals, with a focus on pacemaking applications.

## Table of Contents
- [Overview](#overview)
- [Scripts](#scripts)
- [Usage](#usage)


## Overview
The project includes various scripts for signal processing tasks such as filtering, feature extraction, and visualization. These scripts are intended to support the understanding and application of advanced signal processing techniques in medical contexts.

## Scripts
Below is a brief description of the scripts in this repository:

1. **`main.py`**: The main script that orchestrates the pacemaker detection algorithm. It loads data, processes signals, classifies pacing peaks, and detects pacemaker settings.

2. **`dataloader.py`**: Handles importing and restructuring of `.mat` data files. It also provides functionality for user input to select data and specify whether the signal contains atrium flutter.

3. **`detect_pulses.py`**: Contains functions to filter raw data, detect pacemaker pulses, and remove pacemaker pulses from the signal for further analysis.

4. **`pantompkins.py`**: Implements the Pan-Tompkins algorithm for QRS detection, P-wave detection, and classification of pacing peaks into atrial, ventricular, or unknown types.

5. **`detect_setting.py`**: Defines the `PacingDetector` class, which determines the pacemaker settings (e.g., AOO, VOO, DDD) based on the classified pacing data and additional signal characteristics.


## Usage
1. Clone the repository:
     ```bash
     git clone https://github.com/Ming842/TM12005-E2.git
     cd TM12005-E2
     ```
2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
3. Run the desired script:
     ```bash
     python main.py --input_dir "C:\example\dir\data"
     ```

