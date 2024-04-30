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
        dir_dict (dict): A dictionary containing the data sensor path.
        mod (str, optional): A modifier for the data gathering process.

    Returns:
        None

    Raises:
        SystemExit: If a sensor is not recognized.

    """
    for sensor in os.listdir(dir_dict['data']):
        print(f'Processing {sensor} data...')
        gather_sensor_dir = os.path.join(dir_dict['gather'], sensor)
        create_directory(gather_sensor_dir)
        sensor_dir = os.path.join(dir_dict['data'], sensor)
        for sensor_file in os.listdir(sensor_dir):
            if sensor_file.endswith('.csv'):
                    source_file_path = os.path.join(sensor_dir, sensor_file)
                        
                    # Determine the number of header rows
                    header_rows = count_header_rows(source_file_path)
                        
                    # Process the header
                    df_header = process_header(source_file_path, header_rows)
                        
                    # Process the body
                    df_body = process_body(source_file_path, header_rows, df_header.columns.tolist())

                    # Save the processed data
                    name = sensor_file.split('_')[-1][:-4]
                    dest_file_path = os.path.join(gather_sensor_dir, name)
                    create_directory(dest_file_path)    
                    df_header.to_csv(f'{os.path.join(dest_file_path, 'header.csv')}', index=False, header=False)
                    df_body.to_csv(f'{os.path.join(dest_file_path, 'body.csv')}', index=False, header=True)
                    break
                


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
    columns_to_keep = [df_header.columns[i-1] for i in columns_to_keep]

    # Drop the unselected columns
    df_header = df_header[columns_to_keep]

    return df_header

def process_body(file_path, header_rows, column_headers):
    df_body = pd.read_csv(file_path, skiprows=header_rows, header=0, low_memory=False)

    # Ask the user to select which columns to keep
    columns_to_keep = input("Enter the numbers of the columns to keep, separated by commas (use a dash to specify a range): ")

    # Process the input
    columns_to_keep = process_input(columns_to_keep)
    columns_to_keep = [df_body.columns[i-1] for i in columns_to_keep]

    # Drop the unselected columns
    df_body = df_body[columns_to_keep]

    return df_body

def process_input(user_input):
    user_input = user_input.split(",")
    user_input = [range(int(x.split("-")[0]), int(x.split("-")[1])+1) if "-" in x else int(x) for x in user_input]
    user_input = [item for sublist in user_input for item in sublist]  # Flatten the list
    return user_input


def create_directory(path):
    """Recursively creates a directory if it does not exist."""
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if len(path.split(os.sep)) > 2:
                response = input(f"The path '{path}' does not exist. Do you want to create it? [(0)No/(1)Yes]: ")
                if response == '1':
                    create_directory(os.path.dirname(path))
                    create_directory(path)
                else:
                    sys.exit('Directory creation cancelled.')
            else:
                sys.exit(f"Failed to create directory: {e}")

def rename_files(sensor_dir, new_name):
    """Renames a directory and all files in it based on the new name."""
    new_dir = sensor_dir.parent / new_name
    sensor_dir.rename(new_dir)
    for file in new_dir.iterdir():
        name, ext = file.stem, file.suffix
        name = name.split('_')[-1]
        new_file_name = f"{new_name}_{name}{ext}"
        file.rename(new_dir / new_file_name)

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
                user_dir = Path.home() / {0: 'Desktop', 1: 'Documents', 2: 'Downloads'}.get(int(input('Please select where you would like the results to be stored:\n\t(0) Desktop\n\t(1) Documents\n\t(2) Downloads\nPlease select where you would like the results to be stored: ')))
                create_directory(user_dir)
                export_dir = user_dir / 'iMotionsData'
                if export_dir.exists():
                    shutil.rmtree(export_dir)
                create_directory(export_dir)
                create_directory(export_dir / 'Results')
                create_directory(export_dir / 'Gather')
                shutil.copytree(import_dir, export_dir / 'Data')

                print(f'\nResults Directory: {export_dir}')
                dir_dict = {'exports': export_dir, 'results': export_dir / 'Results', 'gather': export_dir / 'Gather', 'data': export_dir / 'Data'}

                sensor_list = [x for x in dir_dict['data'].iterdir() if x.is_dir()]

                for sensor in sensor_list:
                    for sensor_type, sensor_names in recognized_sensors.items():
                        if any(sensor_name in sensor.name for sensor_name in sensor_names):
                            rename_files(sensor, sensor_type)
                            break
                    else:
                        print(f'Warning: ({sensor.name}) not recognized')
                return dir_dict
    return sys.exit('No import directory, exiting...')

if __name__ == '__main__':
    dir_dict = prep_data()
    gather_data(dir_dict)
