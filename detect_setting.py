import numpy as np
import pandas as pd


class PacingDetector:
    """
    A class to detect the pacing settings based on the classifier data.

    """


    def __init__(self, data, p_mask, contains_atrium_fibrilation):
        self.data = data
        self.frequency_ventricular_pacing = None
        self.frequency_atrial_pacing = None
        self.timedelay_between_atrial_ventricular = None
        self.p_mask = p_mask
        self.contains_atrium_fibrilation = contains_atrium_fibrilation

    def detect_setting(self):
        """
        This function detects the pacing settings based on the classifier data.
        This function is based on the classifier three provided in the report.
        """
        # Check if there was pacing in atrium, ventricle, or both
        if self.contains_atrium_fibrilation:
            atrial_pacing_bool = False
        else: 
            atrial_pacing_bool = (self.data.groupby('type').size().loc["Atrial"] / len(self.data) * 100) > 0.1
        

        ventricular_pacing_bool = (self.data.groupby('type').size().loc["Ventricular"] / len(self.data) * 100) > 0.1


        # Determine the pacing setting based on the detected types
        if atrial_pacing_bool and ventricular_pacing_bool:
            setting = self.dual_pacing()
        elif atrial_pacing_bool:
            setting = self.atrial_pacing()
        elif ventricular_pacing_bool:
            setting = self.ventricular_pacing()
        else:
            return "No pacing detected"
        
        ## Check the frequency for the atrial and ventricular pacing if needed
        message_setting = f"Detected setting: {setting}"
        message_frequency_ventricular = ""
        message_frequency_atrial = ""
        message_time_delay_atrial_ventrikel = ""

        if self.frequency_ventricular_pacing is not None:
            message_frequency_ventricular = (
                "The frequency of the ventricular pacing is mostly between "
                f"{self.frequency_ventricular_pacing[0]:.2f} and {self.frequency_ventricular_pacing[1]:.2f} paces per min"
                )
        if self.frequency_atrial_pacing is not None:
            message_frequency_atrial = (
                ", the frequency of the atrial pacing is mostly between " 
                f"{self.frequency_atrial_pacing[0]:.2f} and {self.frequency_atrial_pacing[1]:.2f} paces per min"
                )
        if self.timedelay_between_atrial_ventricular is not None:
            message_time_delay_atrial_ventrikel = (
                ", the time delay between the atrial and ventricular pacing is mostly between "
                f"{self.timedelay_between_atrial_ventricular[0]:.2f} and {self.timedelay_between_atrial_ventricular[1]:.2f} ms"
                )


        #return the setting and the frequency of the pacing
        return f"{message_setting} {message_frequency_ventricular} {message_frequency_atrial} {message_time_delay_atrial_ventrikel}"

    def check_if_time_between_pulses_is_the_same(self, pulse_type):
        """
        This fuction checks if the time between the pulses in the same.
        Input:
            pulse_type: the type of the pulse to check for (Atrial or Ventricular)

        Output:
            True if the time between the pulses is within 25ms difference 90% of the time, False otherwise.
        """
        # Filter the data for the specified pulse type
        data_filtered = self.data[self.data['type'] == pulse_type]

        # Calculate differences directly
        diffs = data_filtered["index"].diff()

        # Precompute bins with a 25 ms range
        min_diff = diffs.min()
        max_diff = diffs.max()
        bins = np.arange(min_diff, max_diff + 5, 5)  # 25 ms bins

        # Bin the differences
        binned_diff = pd.cut(diffs, bins=bins)

        # Calculate the frequency of the most used bin
        max_bin_count = binned_diff.value_counts().max()
        index_max_bin_count = binned_diff.value_counts().idxmax()
        frequency = [(1/(index_max_bin_count.right/200))*60, (1/(index_max_bin_count.left/200))*60]

        # Store the frequency of each pulse type
        if pulse_type == 'Ventricular' and self.frequency_ventricular_pacing is None:
            self.frequency_ventricular_pacing = frequency
        if pulse_type == 'Atrial' and self.frequency_atrial_pacing is None:
            self.frequency_atrial_pacing = frequency
        # Check if 90% of the time between pulses is within 25 ms difference
        return (max_bin_count / len(data_filtered) * 100) > 90

    def check_if_time_between_ptop_and_pulse_is_the_same(self):
        """
        This function checks if the time between the p-top and the pulse is the same.
        and returns True if 90% of the time between p-top and pulse is within 25 ms difference.
        """

        p_idx = np.where(self.p_mask==True)
        puls_ventricular_idx = self.data[self.data['type'] == "Ventricular"]["index"].to_numpy()

        # Create a DataFrame for p_idx with type "ptop"
        df_p_idx = pd.DataFrame({
            'value': p_idx[0],
            'type': 'ptop'
        })

        # Create a DataFrame for puls_ventricular_idx with type "puls"
        df_puls_ventricular_idx = pd.DataFrame({
            'value': puls_ventricular_idx,
            'type': 'puls'
        })

        # Concatenate the two DataFrames
        df = pd.concat([df_p_idx, df_puls_ventricular_idx], ignore_index=True)
        df.sort_values(by="value", inplace=True, ascending=True)
        df.reset_index(drop=True, inplace=True)

        # Calculate differences directly
        diffs = df["value"].diff()

        # Precompute bins with a 25 ms range
        min_diff = diffs.min()
        max_diff = diffs.max()
        bins = np.arange(min_diff, max_diff + 5, 5)  # 25 ms bins

        # Calculate the frequency of the most used bin
        max_bin_count = binned_diff.value_counts().max()
        index_max_bin_count = binned_diff.value_counts().idxmax()
        time_delay = [(1/(index_max_bin_count.right/200)), (1/(index_max_bin_count.left/200))]

        self.timedelay_between_atrial_ventricular = time_delay

        # Bin the differences
        binned_diff = pd.cut(diffs, bins=bins)
        max_bin_count = binned_diff.value_counts().max()

        # return if 90% of the time between p-top and pulse is within 25 ms difference
        return (max_bin_count / len(df) * 100) > 90

    def dual_pacing(self):
        """
        This function determines a dual pacing setting based on the classifier data
        and returns the setting.
        """
        # Check if time between all pacing peaks is the same. if true, return DDO, else DDD
        if self.check_if_time_between_pulses_is_the_same('Ventricular'):
            if self.check_if_time_between_pulses_is_the_same('Atrial'):
                return "DDO"
            else:
                return "DDD"
        else:
            self.check_if_time_between_pulses_is_the_same('Atrial') # to calculate the frequency of the atrial pacing
            return "DDD"

    def atrial_pacing(self):
        """
        This function determines an atrial pacing setting based on the classifier data
        and returns the setting.
        """
        # Check if time between all atrial pacing peaks is the same. if true, return AOO, else AAI
        if self.check_if_time_between_pulses_is_the_same('Atrial'):
            return "AOO"
        else:
            return "AAI"

    def ventricular_pacing(self):
        """
        This function determines a ventricular pacing setting based on the classifier data
        and returns the setting.
        """

        # First check if the time between all ventricular pacing peaks is the same. if true, return VOO.
        # else it checks if time between p-top and pulse is always the same. If true, returns VAT, else VVI
        if self.check_if_time_between_pulses_is_the_same('Ventricular'):
            return "VOO"
        elif self.check_if_time_between_ptop_and_pulse_is_the_same():
            return "VAT"
        else:
            return "VVI"

