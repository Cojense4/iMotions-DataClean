import shutil
import pandas as pd
from pathlib import Path

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

def get_import_directory():
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
            if new_file_name == 'Survey_desktop.ini.csv':
                raise ValueError(f"IDK WHAT THIS IS??: {file_name}")
        else:
            new_file_name = f"{sensor_type[0]}_{file_name_split[-1]}.csv"
        file_path.rename(Path(file_path.parent / new_file_name))

def prepare_data():
    """
    Prepares the data by setting up directories, copying data, and organizing sensor files.

    Returns:
        tuple: A tuple containing:
            - exports_directory (Path): Path to the exports directory.
            - data_directory (Path): Path to the data directory.
    """

    import_directory = get_import_directory()
    export_directory = get_export_directory()

    data_directory = Path(export_directory / "Data")
    if data_directory.exists():
        keep_previous_data = input("Do you want to keep the previous data? (1)Yes/(ENTER)No: ")
        if keep_previous_data.lower() != "yes" and keep_previous_data != "1":
            shutil.rmtree(data_directory)
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
    index_max = 40
    current_index = 0
    # Read one row, skipping the specified number of rows
    df = pd.read_csv(file_path, low_memory=False)
    try:
        while current_index < index_max:
            # Check if the DataFrame is empty
            if df.empty:
                print(f"Warning: No data found at skiprows={current_index}.")
                current_index += 1
                continue
            
            # Check the first cell data
            first_cell_data = df.iloc[current_index, 0]
            if first_cell_data == "#DATA" or first_cell_data == "question_number":
                return current_index + 2

            current_index += 1
        
        raise Exception( "Error: Could not find the end of the header rows.")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None  # or raise an exception if preferred
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
        return None
    except pd.errors.ParserError as pe:
        print(f"Error processing file {file_path}: {pe}\n")
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

def gather_data(exports):
    """
    Gathers and processes data from sensor directories and organizes the results.
    Args:
        exports (Path): The path to the exports directory where results will be saved.
    Returns:
        Path: The path to the results directory where processed data is saved.
    """
    def create_new_directory(new_path):
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path
    
    results_directory = create_new_directory(exports / 'Results')
    
    # Dictionary to store start indices for each sensor
    data_start_indices = {}
    data_directory = exports / "Data"
    for sensor_directory in data_directory.iterdir():
        sensor_results_dir = create_new_directory(results_directory / sensor_directory.name)
        keep_columns = column_selection(sensor_directory.name)
        
        # Call data_index_finder once for the current sensor and store the result
        sensor_files = list(sensor_directory.iterdir())
        data_index = data_index_finder(sensor_directory / sensor_files[0].name)  # Assuming sensor_directory is a Path
        data_start_indices[sensor_directory.name] = data_index  # Store the index
        
        for file in sensor_files:
            if data_index is not None:  # Ensure data_index is valid before processing
                process_file(file, sensor_results_dir / file.name, keep_columns, data_index)
            else:
                print(f"Skipping file {file} due to invalid data index.")
    
    return results_directory

def process_file(file_path, output_path, keep_columns, data_index):
    """
    Processes a single file by reading the relevant columns and saving the cleaned data.
    Args:
        file_path (Path): The path to the input file to be processed.
        output_path (Path): The path where the processed file will be saved.
        keep_columns (list): A list of columns to keep from the input file.
        data_index (int): The row index where the data starts.
    Raises:
        ValueError: If there's an issue processing the file (e.g., invalid column indices).
    """
    try:
        dataframe_header = pd.read_csv(file_path, skiprows=data_index, nrows=1)
        dataframe_info = pd.read_csv(file_path, nrows=data_index, header=data_index)
        dataframe_body = pd.read_csv(file_path, skiprows=data_index, header=0, usecols=keep_columns, low_memory=False)
        print(dataframe_info,"\n")
        print(dataframe_body)
        pd.concat([dataframe_info, dataframe_body],axis=0).to_csv(output_path, index=False)
    except ValueError as error:
        print(f"Error processing file {file_path}: {error}")

if __name__ == '__main__':
    exports = prepare_data()
    gather_data(exports)
