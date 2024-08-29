import os
import sys
import shutil
import pandas as pd
from pathlib import Path

def load_sensor_config(config_path='SENSORS_config.json'):
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['RECOGNIZED_SENSORS'], config['SENSOR_STIMULUS']

RECOGNIZED_SENSORS, SENSOR_STIMULUS = load_sensor_config()

def create_new_directory(new_path):
    new_path.mkdir(parents=True, exist_ok=True)
    return new_path

def prepare_data():
    home_dir = Path.home()
    
    import_directory = get_import_directory(home_dir)
    exports_directory, data_directory = create_data_directory()

    overwrite_directory(import_directory, data_directory)
    rename_and_organize_sensors(data_directory)

    return exports_directory, data_directory

def get_import_directory(home_dir):
    available_directories = [path for path in home_dir.iterdir() if have_dir_access(path)]
    
    print('-' * 50)
    print("Available IMPORT directories:")
    for index, directory in enumerate(available_directories, start=0):
        print(f"{index}. {directory}")
    
    while True:
        try:
            user_input = int(input("Use Directory [number]: "))
            return available_directories[user_input]
        except (ValueError, IndexError):
            print("Invalid input, please try again.")

def create_data_directory():
    print('-' * 50)
    study_name = "_".join(input("Please name your study: ").split(" ")) or "iMotions_Exports"
    folder_name = study_name + "_Exports"
    
    export_options = [Path.home() / "Downloads" / folder_name,
                      Path.home() / "Desktop" / folder_name,
                      Path.home() / "Documents" / folder_name]

    print("Available EXPORT directories:")
    for i, path in enumerate(export_options):
        print(f'{i}. {path}')
    
    while True:
        try:
            user_choice = int(input("Choose Directory: "))
            exports_directory = create_new_directory(export_options[user_choice])
            data_directory = create_new_directory(exports_directory / 'Data')
            return exports_directory, data_directory
        except (ValueError, IndexError):
            print("Invalid input, please try again.")

def have_dir_access(path):
    try:
        for _ in path.iterdir():
            return True
    except (PermissionError, NotADirectoryError):
        return False

def overwrite_directory(import_directory, data_directory):
    if data_directory.exists():
        while True:
            try:
                remove_previous_data = bool(int(input("Do you want to delete the previous data? (0)NO/(1)YES: ")))
                if remove_previous_data:
                    shutil.rmtree(data_directory)
                    shutil.copytree(import_directory, data_directory)
                break
            except ValueError:
                print("Invalid input, please try again.")

def rename_and_organize_sensors(data_directory):
    for directory in data_directory.iterdir():
        print(directory)
        # Only process directories with 'data' or 'results' in the name
        if 'data' in directory.name.lower() or 'results' in directory.name.lower():
            print(directory.name.lower())
            for sensor_type, sensor_names in RECOGNIZED_SENSORS.items():
                if any(sensor_keyword in directory.name for sensor_keyword in sensor_names):
                    new_directory = data_directory / sensor_type
                    directory.rename(new_directory)
                    for file_name in new_directory.iterdir():
                        rename_file(file_name, sensor_type)
                    break
            else:
                print(f'Warning: ({directory.name}) not recognized or already created')
        else:
            print(f'Skipping folder: ({directory.name}) as it does not contain "data" or "results".')

def rename_file(file_path, sensor_type):
    name, ext = file_path.stem, file_path.suffix
    name_split = name.split('_')
    if name_split[-1].isalpha():
        new_name = f"FBL_{name_split[0]}{ext}"
    else:
        new_name = f"{sensor_type[0]}_{name_split[-1]}{ext}"
    file_path.rename(file_path.parent / new_name)


def data_index_finder(file_path):
    data_start_index = 0
    found_start = False
    
    while not found_start:
        try:
            first_cell_data = pd.read_csv(file_path, nrows=1, skiprows=data_start_index).iloc[0, 0]
                
            # Detect the start of the data based on "question_number" or "#DATA"
            if first_cell_data == 'question_number':
                found_start = True
            elif first_cell_data == '#DATA':
                found_start = True
                # Move one more row down to skip the #DATA row
                data_start_index += 1

            data_start_index += 1
            
        except pd.errors.EmptyDataError:
            print("Error: Could not find the 'question_number' or '#DATA' header.")
            return 0
        
        # The data starts right after the detected header row
        return data_start_index

def column_selection(sensor_name):
    automatic_header_list = SENSOR_STIMULUS[sensor_name]
    try:
        user_selection = int(input(f"Would you like to manually select data columns for '{sensor_name.upper()}' (1)YES/(ENTER)NO: "))
    except ValueError:
        user_selection = 0

    if user_selection:
        for index, header in enumerate(automatic_header_list):
            print(f'{index}. {header}')
        user_header_selection = input(f"Provide indices to keep for data [0-{index}]: ").split(',')
        user_header_list = parse_user_selection(user_header_selection, automatic_header_list)
        return user_header_list if user_header_list else automatic_header_list

    return automatic_header_list

def parse_user_selection(user_selection, header_list):
    indices = []
    for item in user_selection:
        if '-' in item:
            start, end = map(int, item.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(item))
    return [header_list[i] for i in sorted(set(indices)) if 0 <= i < len(header_list)]

def gather_data(exports_directory, data_directory):
    results_directory = create_new_directory(exports_directory / 'Results')
    
    for sensor_name in data_directory.iterdir():
        sensor_results_dir = create_new_directory(results_directory / sensor_name.name)
        keep_columns = column_selection(sensor_name.name)
        
        for file_name in sensor_name.iterdir():
            process_file(file_name, sensor_results_dir / file_name.name, keep_columns)
    
    return results_directory

def process_file(file_path, output_path, keep_columns):
    data_index = data_index_finder(file_path)
    try:
        dataframe = pd.read_csv(file_path, skiprows=data_index, header=0, usecols=keep_columns, low_memory=False)
        dataframe.to_csv(output_path, index=False)
    except ValueError as error:
        print(f"Error processing file {file_path}: {error}")
    def columnSelection(sensorName):
        automaticHeaderList = SENSOR_STIMULUS[sensorName]
        try:
            userSelection = int(input(f"Would you like to manually select data columns for '{sensorName.upper()}' (1)YES/(ENTER)NO: "))
        except:
            userSelection = 0
        
        if userSelection != 0:
            for index, header in enumerate(automaticHeaderList):
                print(f'{index}. {header}')
            userHeaderSelection = input(f"Provide indecies to keep for data [0-{index}]: ").split(',')
            if userHeaderSelection != ['0'] and len(userHeaderSelection) > 1:
                userHeaderSelection = [range(int(x.split("-")[0]), int(x.split("-")[1])) if "-" in x else [int(x)] for x in userHeaderSelection]
                userHeaderSelection = sorted(set([item for sublist in userHeaderSelection for item in sublist]))  # Flatten the list
                userHeaderList = [automaticHeaderList[col] for col in userHeaderSelection]
                return userHeaderList
        return automaticHeaderList


if __name__ == '__main__':
    exports_directory, data_directory = prepare_data()
    print(gather_data(exports_directory, data_directory))
    #TODO: Turn this program into an application for easier user experience
