import shutil
from logging import raiseExceptions
import numpy as np
import pandas as pd
from pathlib import Path
import re

def load_sensor_config(config_path='SENSORS_config.json'):
    """
    Loads the sensor configuration from a JSON file.

    Parameters:
        config_path (str): Path to the sensor configuration file.
    
    Returns:
        tuple: A tuple containing:
            - RECOGNIZED_SENSORS (dict): Dictionary mapping sensor types to their recognized names.
            - SENSOR_STIMULUS (dict): Dictionary mapping sensor types to their corresponding stimuli.
    """
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['RECOGNIZED_SENSORS'], config['SENSOR_STIMULUS']
# Load recognized sensors and their stimuli.
RECOGNIZED_SENSORS, SENSOR_STIMULUS = load_sensor_config()

def get_directory_by_name():
    """
    Prompts the user to select an import directory.

    Returns:
        Path: The selected directory.
    """
    def find_import_directory(search_directory, depth=0, max_depth=2):
        def have_dir_access(path):
            try:
                for _ in path.iterdir():
                    return True
            except (PermissionError, NotADirectoryError):
                return False

        import_directories = []

        if depth > max_depth:
            return import_directories

        if ('data' in search_directory.name.lower()) or ('results' in search_directory.name.lower()):
            if search_directory.name.lower() != "appdata":
                import_directories.append(search_directory)

        for sub_directory in [path for path in Path(search_directory).iterdir() if
                              path.is_dir() and have_dir_access(path)]:
            import_directories.extend(find_import_directory(sub_directory, depth + 1, max_depth))
        return import_directories

    available_directories = find_import_directory(search_directory=Path.home())
    if not available_directories:
        print("No directories containing 'data' or 'results' found.")
        return None
    print('-' * 50)
    print("Available IMPORT directories:")
    for index, directory in enumerate(available_directories, start=1):
        print(f"{index}. {directory}")

    try:
        import_directory = available_directories[int(input("Use Directory [number]: "))-1]
    except (IndexError, ValueError):
        import_directory = available_directories[0]
    return import_directory

def get_export_directory():
    """
    Prompts the user to name their study and select an export directory.

    Returns:
        exports_directory (Path): The created export directory.
    """
    print('-' * 50)
    study_name = ("_".join(input("Please name your study: ").split(" ")) or "Study") + "_EXPORTS"

    available_directories = [Path(Path.home() / "Downloads" / study_name),
                             Path(Path.home() / "Desktop" / study_name),
                             Path(Path.home() / "Documents" / study_name)]

    print("Available EXPORT directories:")
    for index, directory in enumerate(available_directories, start=1):
        print(f"{index}. {directory}")

    try:
        export_directory = available_directories[int(input("Use Directory [number]: "))-1]
    except (IndexError, ValueError):
        export_directory = available_directories[0]
    return export_directory

def rename_files(sensor_directory, sensor_type):
    for file_path in sensor_directory.iterdir():
        file_path = Path(file_path)
        file_name = file_path.name
        file_name_split = file_name.split('_')
        if file_name_split[-1][0].isalpha():
            new_file_name = f"Survey_{file_name_split[0]}.csv"
            if new_file_name == 'Survey_desktop.ini':
                raise ValueError(f"IDK WHAT THIS IS??: {file_name}")
        else:
            new_file_name = f"{sensor_type[0]}_{file_name_split[-1]}"
        file_path.rename(Path(file_path.parent / new_file_name))

def prepare_data():
    """
    Prepares the data by setting up directories, copying data, and organizing sensor files.

    Returns:
        tuple: A tuple containing:
            - exports_directory (Path): Path to the exports' directory.
            - data_directory (Path): Path to the data directory.
    """

    import_directory = get_directory_by_name()
    export_directory = get_export_directory()

    data_directory = Path(export_directory / "Data")
    if data_directory.exists():
        keep_previous_data = input("Do you want to keep the previous data? (1)Yes/(ENTER)No: ")
        if keep_previous_data.lower() != "yes" and keep_previous_data != "1":
            shutil.rmtree(data_directory, ignore_errors=True)
            shutil.copytree(import_directory, data_directory)
    else:
        shutil.copytree(import_directory, data_directory)

    for sensor_directory in data_directory.iterdir():
        for sensor_type, sensor_names in RECOGNIZED_SENSORS.items():
            if any(sensor_keyword.lower() in sensor_directory.name.lower() for sensor_keyword in sensor_names):
                sensor_directory = sensor_directory.rename(data_directory / sensor_type)
                rename_files(sensor_directory, sensor_type)
    return export_directory


def data_index_finder(file_path):
    """
    Finds the starting index of data within a CSV file.

    Parameters:
        file_path (Path): The path of the CSV file.

    Returns:
        int: The row index where the data starts.
    """
    index_max = 50  # Maximum number of rows to check for data
    current_index = 0

    # Read the file without assuming any row is a header
    try:
        df = pd.read_csv(file_path, low_memory=False, header=None, on_bad_lines="skip")
        print(f"File {file_path} loaded successfully.")

        # Check if the file has only 2 columns (potential issue)
        if df.shape[1] == 2:
            print(f"Warning: File {file_path} has only two columns. Trying to correct...")
            column_names = SENSOR_STIMULUS['FBLMist']
            df = pd.read_csv(file_path, low_memory=False, header=None, names=column_names, on_bad_lines="skip")

        # Iterate through rows to find the data start
        while current_index < min(index_max, len(df)):
            first_cell = df.iloc[current_index, 0]  # Get the first cell of the current row

            # Skip empty or NaN rows
            if pd.isna(first_cell):
                current_index += 1
                continue

            # Check if the row contains specific markers indicating the start of the data
            if first_cell == "#DATA" or first_cell == "sona_id":
                print(f"Data starts at row {current_index + 1}")
                return current_index + 1

            current_index += 1

        raise Exception("Error: Could not find the start of the data.")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
        return None
    except pd.errors.ParserError as pe:
        print(f"Error processing file {file_path}: {pe}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def column_selection(sensor_name):
    """
    Prompts the user to manually select data columns or use predefined selections.

    Parameters:
        sensor_name (str): The name of the sensor.

    Returns:
        list: A list of column names to keep in the data.
    """
    automatic_header_list = SENSOR_STIMULUS[sensor_name]
    try:
        user_selection = int(input(f"Would you like to manually select data columns for '{sensor_name.upper()}' (1)YES/(ENTER)NO: "))
    except ValueError:
        user_selection = 0

    if user_selection:
        index = 0
        for index, header in enumerate(automatic_header_list):
            print(f'{index}. {header}')
        user_header_selection = input(f"Provide indices to keep for data [0-{index}]: ").split(',')
        user_header_list = parse_user_selection(user_header_selection, automatic_header_list)
        return user_header_list if user_header_list else automatic_header_list

    return automatic_header_list

def parse_user_selection(user_selection, header_list):
    """
    Parses the user's column selection input into a list of column names.

    Parameters:
        user_selection (list): List of user-selected column indices or ranges.
        header_list (list): List of available column names.

    Returns:
        list: A list of selected column names.
    """
    indices = []
    for item in user_selection:
        if '-' in item:
            start, end = map(int, item.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(item))
    return [header_list[i] for i in sorted(set(indices)) if 0 <= i < len(header_list)]

def gather_data(export_dir):
    """
    Gathers and processes data from sensor directories and organizes the results.
    Args:
        export_dir (Path): The path to the exports directory where results will be saved.
    Returns:
        Path: The path to the results directory where processed data is saved.
    """
    def create_new_directory(new_path):
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path
    
    results_dir = create_new_directory(export_dir / 'Results')
    
    # Dictionary to store start indices for each sensor
    data_start_indices = {}
    data_directory = export_dir / "Data"
    for sensor_directory in data_directory.iterdir():
        sensor_results_dir = create_new_directory(results_dir / sensor_directory.name)
        keep_columns = column_selection(sensor_directory.name)
        
        # Call data_index_finder once for the current sensor and store the result
        sensor_files = list(sensor_directory.iterdir())
        data_index = data_index_finder(sensor_files[0])  # Assuming sensor_directory is a Path
        data_start_indices[sensor_directory.name] = data_index  # Store the index
        
        for file in sensor_files:
            if data_index is not None:  # Ensure data_index is valid before processing
                process_file(file, sensor_results_dir / file.name, keep_columns, data_index)
            else:
                print(f"Skipping file {file} due to invalid data index.")
    
    return results_dir

def process_file(file_path, output_path, keep_columns, data_index, retry=True):
    """
    Processes a single file by reading the relevant columns and saving the cleaned data.
    Args:
        retry: retries the process_file function once to see if it can find the correct index
        file_path (Path): The path to the input file to be processed.
        output_path (Path): The path where the processed file will be saved.
        keep_columns (list): A list of columns to keep from the input file.
        data_index (int): The row index where the data starts.
    Raises:
        ValueError: If there's an issue processing the file (e.g., invalid column indices).
    """

    def read_csv_with_fixed_columns(file, column_names=None, num_columns=6):
        # Create column names to force 6 columns
        if column_names is None:
            column_names = [f"Column_{i}" for i in range(1, num_columns + 1)]

        # Read the CSV, forcing the specified number of columns
        df = pd.read_csv(file, header=None, names=column_names, engine='python', on_bad_lines='skip')

        # Pad rows with fewer columns
        if df.shape[1] < num_columns:
            for i in range(num_columns - df.shape[1]):
                df[f'Extra_Column_{i + 1}'] = pd.NA

        # Truncate rows with more columns
        if df.shape[1] > num_columns:
            df = df.iloc[:, :num_columns]

        return df

    try:
        if retry:
            # Read the body of the data
            dataframe_body = pd.read_csv(file_path, skiprows=data_index, header=0, low_memory=False)
        else:
            column_names = SENSOR_STIMULUS['FBLMist']
            dataframe_body = read_csv_with_fixed_columns(file_path, column_names)

        # Handle case when the DataFrame has only two columns
        if dataframe_body.shape[1] == 2:
            print(f"Warning: Detected only two columns in {file_path}. Attempting to process all data.")
            if retry:
                # Retry with a new data index (this could be an automatic fix if needed)
                new_data_index = data_index_finder(file_path)
                return process_file(file_path, output_path, keep_columns, new_data_index, retry=False)
            else:
                # If retry fails, just process all columns and issue a warning
                existing_columns = dataframe_body.columns.tolist()
                print(f"Processing all available columns: {existing_columns}")

        existing_columns = [col for col in keep_columns if col in dataframe_body.columns]
        if not existing_columns:
            if retry:
                new_data_index = data_index_finder(file_path)
                return process_file(file_path, output_path, keep_columns, new_data_index, retry=False)
            else:
                existing_columns = dataframe_body.columns.tolist()
                print(f"Warning: None of the keep_columns are found in {file_path}. Processing all columns.")
                print(f'Header Row Used: {existing_columns}')
                print(f'-' * 40)

        dataframe_body = dataframe_body[existing_columns]  # Keep only the specified columns


        # Read the header part of the data
        dataframe_header = pd.read_csv(file_path, nrows=data_index, header=None)

        # Ensure dataframe_header has exactly 6 columns
        num_columns = 6
        if dataframe_header.shape[1] < num_columns:
            for i in range(num_columns - dataframe_header.shape[1]):
                dataframe_header[f'Extra_Column_{i + 1}'] = np.nan

        # Ensure the number of columns match before assigning the column names
        if len(dataframe_header.columns) != len(dataframe_body.columns):
            dataframe_header = dataframe_header.iloc[:, :len(dataframe_body.columns)]  # Trim to match

        # Rename the columns in dataframe_header to match the data columns
        header_columns = dataframe_body.columns.to_list()

        dataframe_header.columns = header_columns

        # Concatenate header and body
        final_dataframe = pd.concat([dataframe_header, dataframe_body], axis=0, ignore_index=True)

        # Save the processed data
        final_dataframe.to_csv(output_path, index=False)

    except KeyError as ke:
        print(ke)
        new_data_index = data_index_finder(file_path)
        print(new_data_index)
        return process_file(file_path, output_path, keep_columns, new_data_index+1)



if __name__ == '__main__':
    exports = prepare_data()
    results_directory = gather_data(exports)
    print(f"Data processing complete. Results saved in: {results_directory}")

