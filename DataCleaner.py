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
def export_data(hidx, start=None, end=None, path=None, R_PATH=None, lbl=False, cols=None):
    pass


def clean_data(r_name=None, r_path=None, g_path=None):
    pass


def gather_data(dir_dict, mod=None):
    """
    Gather and process data from different sensors.

    Args:
        dir_dict (dict): A dictionary containing the data directory path.
        mod (str, optional): A modifier for the data gathering process.

    Returns:
        None

    Raises:
        SystemExit: If a sensor is not recognized.

    """
    data_dir = dir_dict['data']
    for directory in recognized_sensors.keys():
        sensor_dir = data_dir / directory
        if sensor_dir.exists():
            print(f'Processing {directory} data...')
            for file_name in os.listdir(data_dir):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(data_dir, file_name)
                    
                    # Determine the number of header rows
                    header_rows = count_header_rows(file_path)
                    
                    # Process the header
                    df_header = process_header(file_path, header_rows)
                    
                    # Process the body
                    df_body = process_body(file_path, header_rows, df_header.columns.tolist())
                    
                    # Save the processed data
                    df_header.to_csv('header.csv', index=False, header=False)
                    df_body.to_csv('body.csv', index=False, header=True)
                    

                    name = file_name.stem.split('_')[-1]
                    head_name = f"header_{name}.csv"
                    body_name = f"body_{name}.csv"
                    print(head_name, body_name)
                    return
                    df_header.to_csv(head_name, index=False, header=False)
                    df_body.to_csv(body_name, index=False, header=True)
                    break
        else:
            print(f'Warning: {directory} data not found')


def count_header_rows(file_path):
    with open(file_path, 'r') as f:
        header_rows = 0
        for line in f:
            header_rows += 1
            if '#DATA' in line:
                header_rows += 1
                break
    return header_rows

def process_header(file_path, header_rows):
    df_header = pd.read_csv(file_path, nrows=header_rows-2)
    df_header = df_header.transpose()  # Transpose the data
    df_header.columns = df_header.iloc[0]  # Set the first row as column headers

    # Get a list of column headers
    column_headers = df_header.columns.tolist()

    # Print the column headers
    print("Column headers:")
    for i, header in enumerate(column_headers, 1):
        print(f"{i}. {header}")

    # Ask the user to select which columns to keep
    columns_to_keep = input("Enter the numbers of the columns to keep, separated by commas (use a dash to specify a range): ")

    # Process the input
    columns_to_keep = process_input(columns_to_keep)

    # Drop the unselected columns
    df_header = df_header[columns_to_keep]

    return df_header

def process_body(file_path, header_rows, column_headers):
    df_body = pd.read_csv(file_path, skiprows=header_rows, header=0, low_memory=False)

    # Ask the user to select which columns to keep
    columns_to_keep = input("Enter the numbers of the columns to keep, separated by commas (use a dash to specify a range): ")

    # Process the input
    columns_to_keep = process_input(columns_to_keep)

    # Drop the unselected columns
    df_body = df_body[columns_to_keep]

    return df_body

def process_input(user_input):
    user_input = user_input.split(",")
    user_input = [range(int(x.split("-")[0]), int(x.split("-")[1])+1) if "-" in x else int(x) for x in user_input]
    user_input = [item for sublist in user_input for item in sublist]  # Flatten the list
    return user_input


def create_directory(path):
    """Creates a directory if it does not exist."""
    if not path.exists():
        path.mkdir()

def rename_files(sensor_dir, sensor_type):
    """Renames all files in a directory based on the sensor type."""
    for file in sensor_dir.iterdir():
        name, ext = file.stem, file.suffix
        name = name.split('_')[-1]
        new_name = f"{sensor_type}_{name}{ext}"
        file.rename(sensor_dir / new_name)

def prep_data():
    """
    Prepares the data for cleaning and analysis.

    This function prompts the user to select an import directory and a directory to store the results.
    It creates the necessary directories and copies the data from the import directory to the export directory.
    It also renames the files based on the recognized sensors.

    Returns:
        dir_dict (dict): A dictionary containing the paths to the results directory, gather directory, and data directory.
    """
    current_dir = Path.cwd()
    user_dir = None
    while user_dir not in (0, 1):
        directories = [d for d in current_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        for i, directory in enumerate(directories, start=1):
            user_dir = int(input(f'Use "{directory}" ({i}/{len(directories)}) as import directory? [(0)No/(1)Yes]: '))
            if user_dir:
                import_dir = directory
                print(import_dir)
                user_dir = Path.home() / {0: 'Desktop', 1: 'Documents', 2: 'Downloads'}.get(int(input('Please select where you would like the results to be stored:\n\t(0) Desktop\n\t(1) Documents\n\t(2) Downloads\nPlease select where you would like the results to be stored: ')))
                create_directory(user_dir)
                export_dir = user_dir / 'iMotionsData'
                if export_dir.exists():
                    shutil.rmtree(export_dir)
                create_directory(export_dir)
                create_directory(export_dir / 'Results')
                create_directory(export_dir / 'Gather')
                shutil.copytree(import_dir, export_dir / 'test_data')

                print(f'\nResults Directory: {export_dir}')
                dir_dict = {'results': export_dir / 'Results', 'gather': export_dir / 'Gather', 'data': export_dir / 'test_data'}

                sensor_list = [x for x in dir_dict['data'].iterdir() if x.is_dir()]

                for sensor in sensor_list:
                    for sensor_type, sensor_names in recognized_sensors.items():
                        if any(sensor_name in sensor.name for sensor_name in sensor_names):
                            print(f"({sensor.name}) is associated with ({sensor_type})")
                            rename_files(sensor, sensor_type)
                            break
                    else:
                        print(f'Warning: ({sensor.name}) not recognized')
                return dir_dict
    return sys.exit('No import directory, exiting...')

if __name__ == '__main__':
    dir_dict = prep_data()
    gather_data(dir_dict)
