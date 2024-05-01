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

    # Prompt the user to select the import directory
    import_dir = None
    while not import_dir:
        print("Available import directories:")
        directories = [d for d in Path.cwd().iterdir() if d.is_dir() and not d.name.startswith('.')]
        for i, directory in enumerate(directories, start=1):
            print(f"{i}. {directory}")
        user_choice = input("Use Directory [number]: ")
        try:
            user_choice = int(user_choice)
            if 1 <= user_choice <= len(directories):
                import_dir = directories[user_choice - 1]
        except ValueError:
            pass

    # Prompt the user to select the export directory
    export_dir = None
    while not export_dir:
        print("Available export directories:")
        print(f'1. {Path.home() / "Desktop" / "iMotions_Exports"}')
        print(f'2. {Path.home() / "Documents" / "iMotions_Exports"}')
        print(f'3. {Path.home() / "Downloads" / "iMotions_Exports"}')
        user_choice = input("Use Directory [number]: ")
        try:
            user_choice = int(user_choice)
            if user_choice == 1:
                export_dir = Path.home() / "Desktop" / "iMotions_Exports"
            elif user_choice == 2:
                export_dir = Path.home() / "Documents" / "iMotions_Exports"
            elif user_choice == 3:
                export_dir = Path.home() / "Downloads" / "iMotions_Exports"
        except ValueError:
            pass

    dir_dict = {
        'export': export_dir,
        'gather': export_dir / 'Gather',
        'results': export_dir / 'Results',
        'data': export_dir / 'Data'
    }        
    # Create the necessary directories
    create_directory(dir_dict['export'])
    create_directory(dir_dict['gather'])
    create_directory(dir_dict['results'])
    create_directory(dir_dict['data'])

    # Check if the export directory is empty
    if not os.listdir(dir_dict['data']):
        delete_previous_data = 1
    else:
        delete_previous_data = int(input("Do you want to delete the previous data? (0)No/(1)Yes: "))

    if delete_previous_data:
        # Delete the existing data directory
        if os.path.exists(dir_dict['data']):
            shutil.rmtree(dir_dict['data'])
            # Copy the data from the import directory to the export directory
            shutil.copytree(import_dir, dir_dict['data'])
    user_sensors = []
    sensor_list = [x for x in dir_dict['data'].iterdir() if x.is_dir()]
    for sensor in sensor_list:
        for sensor_type, sensor_names in recognized_sensors.items():
            if any(sensor_name in sensor.name for sensor_name in sensor_names):
                user_sensors.append(sensor_type)
                new_dir = sensor.parent / sensor_type
                sensor.rename(new_dir)
                create_directory(dir_dict['gather']/ sensor_type)
                for file in new_dir.iterdir():
                    name, ext = file.stem, file.suffix
                    name = name.split('_')[-1]
                    new_file_name = f"{sensor_type}_{name}{ext}"
                    file.rename(new_dir / new_file_name)
                    create_directory(dir_dict['gather']/ sensor_type / name)
                break
        else:
            sys.exit(f'Warning: ({sensor.name}) not recognized')

    return dir_dict, user_sensors


def gather_data(dir_dict):

    """
    Gather and process data from different sensors.

    Args:
        dir_dict (dict): A dictionary containing the data sensor path.

    Returns:
        None

    Raises:
        SystemExit: If a sensor is not recognized.

    """
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

    def count_header_rows(file_path):
        with open(file_path, 'r') as f:
            header_rows = 0
            for line in f:
                header_rows += 1
                if '#DATA' in line:
                    header_rows += 1
                    break
        return header_rows

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
    
    def process_header(file_path, columns_to_keep=None):
        # Load the data...
        if columns_to_keep is None:
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

        return df_header, columns_to_keep
    
    def process_input(user_input):
        user_input = user_input.split(",")
        user_input = [range(int(x.split("-")[0]), int(x.split("-")[1])+1) if "-" in x else int(x) for x in user_input]
        user_input = [item for sublist in user_input for item in sublist]  # Flatten the list
        return user_input
    
    for sensor in os.listdir(dir_dict['data']):
        columns_to_keep = None
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
                    if columns_to_keep is None:
                        df_header, columns_to_keep = process_header(source_file_path)
                    else:
                        df_header = process_header(source_file_path, columns_to_keep)
                        
                    # Process the body
                    df_body = process_body(source_file_path, header_rows, df_header.columns.tolist())

                    # Save the processed data
                    name = sensor_file.split('_')[-1][:-4]
                    dest_file_path = os.path.join(gather_sensor_dir, name)
                    create_directory(dest_file_path)    
                    df_header.to_csv(f'{os.path.join(dest_file_path, 'header.csv')}', index=False, header=False)
                    df_body.to_csv(f'{os.path.join(dest_file_path, 'body.csv')}', index=False, header=True)
                    break



def clean_data(dir_dict):
    """
    Cleans the gathered data.

    Args:
        dir_dict (dict): A dictionary containing the data sensor path.

    Returns:
        None
    """
    # Your existing code here...
    return None

if __name__ == '__main__':
    dir_dict, sensor_list = prep_data()
    print(sensor_list)