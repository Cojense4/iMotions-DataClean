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
                    new_file_name = f"{sensor_type[0]}_{name}{ext}"
                    file.rename(new_dir / new_file_name)
                break
        else:
            print(f'Warning: ({sensor.name}) not recognized or already created')

    return dir_dict, user_sensors


def gather_data(dir_dict):
    def header_end(f_path):
        header_end_index = 19
        # Check for end of header rows
        header_end = pd.read_csv(file_path, nrows=1, skiprows=header_end_index).iloc[0,0]
        while header_end != '#DATA':
            if header_end_index > 40:
                print("Error: Could not find the end of the header rows.")
                break
            header_end_index += 1
            header_end = pd.read_csv(file_path, nrows=1, skiprows=header_end_index).iloc[0,0]
            
        # Skip the #DATA row and the column headers row
        return header_end_index + 2
    def column_chooser(columns):
        print(columns)
        # TODO: Implement column choosing   
    # Go through each sensor directory
    for sensor in os.listdir(dir_dict['data']):
        sensor_dir = os.path.join(dir_dict['data'], sensor)

        # Go through each file in sensor directory
        for file_name in os.listdir(sensor_dir):
            file_path = os.path.join(sensor_dir, file_name)
            header_end_index = header_end(file_path)

            df_headers = pd.read_csv(file_path, skiprows=header_end_index, header=0, nrows=0, low_memory=False).columns.tolist()
            columns_to_keep = column_chooser(df_headers)
            continue

            # Display the column headers
            print("Here are the column headers:")
            for i, col in enumerate(df.columns, 1):
                print(f"{i}. {col}")

            # Ask the user to select which columns to keep
            user_input = input("Enter the numbers of the columns to keep, comma separated, use dash for range: ")

            # Process the user input
            user_input = user_input.split(",")
            user_input = [range(int(x.split("-")[0]), int(x.split("-")[1])+1) if "-" in x else [int(x)] for x in user_input]
            columns_to_keep = [item for sublist in user_input for item in sublist]  # Flatten the list

            # Keep only the selected columns
            df = df[df.columns[columns_to_keep]]

            return df
                #TODO: Finish this section of the code, should be finding a way to smartly detect which columns to keep based on the data
                #TODO: Also need to add a way to keep the same columns for the next participant if they are the same sensor


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
    gather_data({'export': 'C:/Users/cjensen32/Downloads/iMotions_Exports', 'gather': 'C:/Users/cjensen32/Downloads/iMotions_Exports/Gather', 'results': 'C:/Users/cjensen32/Downloads/iMotions_Exports/Results', 'data': 'C:/Users/cjensen32/Downloads/iMotions_Exports/Data'})