import csv
from pathlib import Path
import os
import sys
import shutil
import pandas as pd
import time

recognized_sensors = {
    'FACET': ['Camera', 'Emotient', 'FACET'],
    'Shimmer': ['Shimmer', 'GSR'],
    'Aurora': ['Eyetracker', 'Smart Eye', 'Aurora'],
    'PolarH10': ['Bluetooth Low Energy', 'Polar H10', 'HeartRate']
}

sensor_stimuli = {
    'FACET': ['SampleNumber', 'Timestamp RAW', 'Timestamp CAL', 'System Timestamp CAL', 'VSenseBatt RAW', 'VSenseBatt CAL', 'Internal ADC A13 PPG RAW', 'Internal ADC A13 PPG CAL', 
              'GSR RAW' , 'GSR Resistance CAL', 'GSR Conductance CAL', 'Heart Rate PPG ALG', 'IBI PPG ALG', 'Packet reception rate RAW'],
    'Shimmer': [],
    'Aurora': [],
    'PolarH10': [],
}
#TODO: Finish adding sensor stimulus to the above dictionary for 'smart' recognition of rows to keep in future updates

def prep_data():
    """
    Prepares the data for cleaning and analysis.

    This function prompts the user to select an import directory and a directory to store the results.
    It creates the necessary directories and copies the data from the import directory to the export directory.
    It also renames the files based on the recognized sensors.

    Returns:
        dir_dict (dict): A dictionary containing the paths to the results directory, gather directory, and data directory.
    """
    def create_directory(path):
        """Recursively creates a directory if it does not exist."""
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as e:
                sys.exit(f"Failed to create directory: {e}")
        else:
            return print(f'"{path}" already exists')
    
    import_dir = None
    export_dir = None
    dir_dict = dict()
    user_sensors = list()

    # Prompt the user to select the import directory
    while not import_dir:
        print('-'*50)
        print("Available IMPORT directories:")
        directories = [d for d in Path.cwd().iterdir() if d.is_dir() and not d.name.startswith('.')]
        for i, directory in enumerate(directories, start=1):
            print(f"{i-1}. {directory}")
        user_choice = input("Use Directory [number]: ")
        try:
            user_choice = int(user_choice)
            if 0 <= user_choice <= len(directories):
                import_dir = directories[user_choice]
        except ValueError:
            continue

    # Prompt the user to select the export directory
    while not export_dir:
        print('-'*50)
        print("Available EXPORT directories:")
        print(f'0. {Path.home() / "Downloads" / "iMotions_Exports"}')
        print(f'1. {Path.home() / "Desktop" / "iMotions_Exports"}')
        print(f'2. {Path.home() / "Documents" / "iMotions_Exports"}')
        user_choice = input("Use Directory [number]: ")
        try:
            user_choice = int(user_choice)
        except:
            user_choice = 0
        finally: 
            if user_choice == 0:
                export_dir = Path.home() / "Downloads" / "iMotions_Exports"
            elif user_choice == 1:    
                export_dir = Path.home() / "Desktop" / "iMotions_Exports"
            elif user_choice == 2:
                export_dir = Path.home() / "Documents" / "iMotions_Exports"
    
    # Dictionary for paths to go for easier reference
    dir_dict.update({'export': export_dir, 'results': export_dir / 'Results', 'data': export_dir / 'Data'})
    
    # Data removal block with error handling
    try: 
        os.listdir(dir_dict['export'])
    except FileNotFoundError as e:
        rm_prev = 0
    else:
        print('-'*50)
        rm_prev = int(input("Do you want to delete the previous data? (0)YES/(1)NO: "))
    finally:
        if not rm_prev:
            if os.path.exists(dir_dict['export']):
                shutil.rmtree(dir_dict['export'])
                # Copy the data from the import directory to the export directory
            shutil.copytree(import_dir, dir_dict['data'])

    # Rename data files and create directories for results/gather data  
    sensor_list = [x for x in dir_dict['data'].iterdir() if x.is_dir()]
    for sensor in sensor_list:
        for sensor_type, sensor_names in recognized_sensors.items():
            if any(sensor_name in sensor.name for sensor_name in sensor_names):
                user_sensors.append(sensor_type)
                new_dir = sensor.parent / sensor_type
                sensor.rename(new_dir)
                e_sensor_dir = os.path.join(dir_dict['results'], sensor_type)
                if not rm_prev:
                    create_directory(e_sensor_dir)
                for file in new_dir.iterdir():
                    name, ext = file.stem, file.suffix
                    name = name.split('_')[-1]
                    new_file_name = f"{sensor_type[0]}_{name}{ext}"
                    file.rename(new_dir / new_file_name)
                break
        else:
            print(f'Warning: ({sensor.name}) not recognized or already created')

    return dir_dict, user_sensors


def gather_data(dir_dict):
    """
    Gets rid of unwanted data selected by user.

    This function prompts the user to indecies for columns of data they would like to keep. 
    The program then uses pandas to efficiently grab that data and exports it to the 'results' directory created by the prep_data() function

    Returns:
        dir_dict['results']: A path object to the results directory.
    """
    def header_end(file_data_path):
        header_end_index = 19
        # Check for end of header rows
        header_end = pd.read_csv(file_data_path, nrows=1, skiprows=header_end_index).iloc[0,0]
        while header_end != '#DATA':
            if header_end_index > 40:
                print("Error: Could not find the end of the header rows.")
                return 21
            header_end_index += 1
            header_end = pd.read_csv(file_data_path, nrows=1, skiprows=header_end_index).iloc[0,0]
            
        # Skip the #DATA row and the column headers row
        return header_end_index + 2
    def column_chooser(df_headers, sensor_name):
        print(f'\n{'-'*25}{sensor_name.upper()} DATA{'-'*25}')
        for i, header in enumerate(df_headers):
            print(f'{i+1}. {header}')
        e = 27
        print('-'*50)
        user_selection = input(f"Provide indecies to keep for '{sensor_name.upper()}' data (stimuli: [1-{e}]) (events: [{e+1}-{i+1}]): ").split(',')
        if user_selection == ['0']:
            user_selection = [item for item in range(1,e+1)]
        else:
            user_selection = [range(int(x.split("-")[0]), int(x.split("-")[1])+1) if "-" in x else [int(x)] for x in user_selection]
            user_selection = sorted(set([item for sublist in user_selection for item in sublist]))  # Flatten the list
        user_col_names = [df_headers[col - 1] for col in user_selection]
        user_col_indexes = [col-1 for col in user_selection]
        return user_col_names, user_col_indexes
        #TODO: fix "['0']" option to use sensor_stimulus dictionary
    
    # Go through each sensor directory
    for sensor in os.listdir(dir_dict['data']):
        sensor_data_dir = os.path.join(dir_dict['data'], sensor)
        sensor_export_dir = os.path.join(dir_dict['results'], sensor)
        keep_cols = None
        
        # Go through each file
        for file_name in os.listdir(sensor_data_dir):
            file_export_path = os.path.join(sensor_export_dir, file_name)
            file_data_path = os.path.join(sensor_data_dir, file_name)
            header_end_index = header_end(file_data_path)

            # Grab header info, then get columns to keep if first file in sensor directory 
            df_headers = pd.read_csv(file_data_path, skiprows=header_end_index, header=0, nrows=0, low_memory=False).columns.tolist()[1:]
            if keep_cols == None:
                keep_cols, keep_cols_index = column_chooser(df_headers, sensor)  
            try:
                df = pd.read_csv(file_data_path, skiprows=header_end_index, header=0, usecols=keep_cols_index, low_memory=False)
            except ValueError as e:
                error_cols = str(e).split(': ')[1]
                e_keep_cols = [col for col in keep_cols if col not in error_cols]
                df = pd.read_csv(file_data_path, skiprows=header_end_index, header=0, usecols=e_keep_cols, low_memory=False)
            finally:
                df.to_csv(file_export_path)
    return dir_dict['results']
    #TODO: Utilize df headers for files to get metadata (find place to put metadata)
    #TODO: Finish this section of the code, should be finding a way to smartly detect which columns to keep based on the data
    #TODO: Also need to add a way to keep the same columns for the next participant if they are the same sensor


if __name__ == '__main__':
    data_dirs, sensors = prep_data()
    results_dir = gather_data(data_dirs)
