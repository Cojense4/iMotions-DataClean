# ==========================
# 1. Import Statements and Global Variables
# ==========================
from tqdm import tqdm
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

# Load recognized sensors and their stimuli globally
RECOGNIZED_SENSORS, SENSOR_STIMULUS = load_sensor_config()


# ==========================
# 2. Directory and File Handling Functions
# ==========================
def create_new_directory(new_path):
    """
    Creates a new directory if it does not exist.

    Parameters:
        new_path (Path): Path object representing the directory to be created.

    Returns:
        Path: The created directory path.
    """
    new_path.mkdir(parents=True, exist_ok=True)
    return new_path

def have_dir_access(path):
    """
    Checks if the directory is accessible.

    Parameters:
        path (Path): Path object representing the directory to check.

    Returns:
        bool: True if the directory is accessible, False otherwise.
    """
    try:
        for _ in path.iterdir():
            return True
    except (PermissionError, NotADirectoryError):
        return False

def find_data_dir(directory, depth=0, max_depth=3):
    """
    Recursively searches for directories with 'data' or 'results' in their names.

    Parameters:
        directory (Path): Path object representing the directory to search.
        depth (int): Current recursion depth.
        max_depth (int): Maximum recursion depth allowed.

    Returns:
        list: A list of directories matching the criteria.
    """
    matching_directories = []

    # Stop recursion if max depth is reached or directory names match exclusions
    if depth > max_depth or 'onedrive' in directory.name.lower() or 'exports' in directory.name.lower():
        return matching_directories

    # Match directories with 'results' in their name
    if 'results' in directory.name.lower():
        matching_directories.append(directory)

    # Recurse through subdirectories
    for sub_directory in [path for path in Path(directory).iterdir() if path.is_dir() and have_dir_access(path)]:
        matching_directories.extend(find_data_dir(sub_directory, depth + 1))

    return matching_directories


# ==========================
# 3. User Interaction and Input Handling
# ==========================
def get_import_directory(home_dir):
    """
    Prompts the user to select an import directory.

    Parameters:
        home_dir (Path): Path object representing the home directory.

    Returns:
        Path: The selected directory.
    """
    available_directories = find_data_dir(home_dir)

    # If no directories found, notify the user
    if not available_directories:
        print("No directories containing 'data' or 'results' found.")
        return None

    # Display available directories and let the user select one
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
    """
    Prompts the user to name their study and select an export directory.

    Returns:
        tuple: A tuple containing:
            - exports_directory (Path): The created exports directory.
            - data_directory (Path): The created data directory within the exports directory.
    """
    print('-' * 50)
    study_name = "_".join(input("Please name your study: ").split(" ")) or "iMotions_Exports"
    folder_name = study_name + "_Exports"

    # Define default export directory options
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


# ==========================
# 4. Data Preparation and Organization
# ==========================
def prepare_data():
    """
    Prepares the data by setting up directories, copying data, and organizing sensor files.

    Returns:
        tuple: A tuple containing:
            - exports_directory (Path): Path to the exports directory.
            - data_directory (Path): Path to the data directory.
    """
    home_dir = Path.home()

    # Select import directory containing the original data
    import_directory = get_import_directory(home_dir)

    # Create export directories based on user input
    exports_directory, data_directory = create_data_directory()

    # Overwrite the data directory with the new import
    overwrite_directory(import_directory, data_directory)

    # Organize and rename sensor files
    rename_and_organize_sensors(data_directory)

    return exports_directory, data_directory

def overwrite_directory(import_directory, data_directory):
    """
    Overwrites the data directory with the contents of the import directory.

    Parameters:
        import_directory (Path): The directory from which data is imported.
        data_directory (Path): The directory to which data is copied.
    """
    if data_directory.exists():
        while True:
            try:
                remove_previous_data = bool(int(input("Do you want to delete the previous data? (0)NO/(1)YES: ")))
                if remove_previous_data:
                    shutil.rmtree(data_directory)  # Delete existing directory
                    shutil.copytree(import_directory, data_directory)  # Copy new data
                break
            except ValueError:
                print("Invalid input, please try again.")

def rename_and_organize_sensors(data_directory):
    """
    Renames and organizes sensor files within the data directory.

    Parameters:
        data_directory (Path): The directory containing sensor data files.
    """
    # Iterate through each subdirectory in the data directory
    for directory in data_directory.iterdir():
        # Check if the directory matches a recognized sensor type
        for sensor_type, sensor_names in RECOGNIZED_SENSORS.items():
            # If any sensor keyword is found in the directory name, rename and organize it
            if any(sensor_keyword in directory.name for sensor_keyword in sensor_names):
                new_directory = data_directory / sensor_type
                directory.rename(new_directory)  # Rename directory to sensor type
                # Rename each file inside the newly created sensor directory
                for file_name in new_directory.iterdir():
                    rename_file(file_name, sensor_type)
                break
        else:
            # Warn if the directory is not recognized or has already been created
            print(f'Warning: ({directory.name}) not recognized or already created')

def rename_file(file_path, sensor_type):
    """
    Renames a file based on the sensor type and its current name.

    Parameters:
        file_path (Path): The path of the file to be renamed.
        sensor_type (str): The type of sensor the file corresponds to.
    """
    # Split the file name into name and extension
    name, ext = file_path.stem, file_path.suffix
    name_split = name.split('_')  # Split the file name by underscores

    # Rename based on the pattern of the file name and the sensor type
    if name_split[-1].isalpha():
        new_name = f"FBL_{name_split[0]}{ext}"
    else:
        new_name = f"{sensor_type[:3].upper()}_{name_split[-1]}{ext}"

    # Rename the file with the new name
    file_path.rename(file_path.parent / new_name)


# ==========================
# 5. Data Processing Functions
# ==========================
def data_index_finder(file_path):
    """
    Finds the starting index of data within a CSV file.

    Parameters:
        file_path (Path): The path of the CSV file.

    Returns:
        int: The row index where the actual data starts.
    """
    index_max = 40  # Maximum number of rows to search for data start
    current_index = 0  # Start index for the search
    df = pd.read_csv(file_path, low_memory=False)  # Load CSV file into a DataFrame

    try:
        # Iterate through the rows until the data start marker is found
        while current_index < index_max:
            if df.empty:
                # If the DataFrame is empty, skip and continue searching
                print(f"Warning: No data found at skiprows={current_index}.")
                current_index += 1
                continue

            # Check the first cell of the current row for data markers
            first_cell_data = df.iloc[current_index, 0]
            if first_cell_data == "#DATA" or first_cell_data == "question_number":
                return current_index + 2  # Return index + 2 for the start of data

            current_index += 1

        # Raise an exception if the data start index is not found
        raise Exception("Error: Could not find the end of the header rows.")

    # Handle various exceptions gracefully and provide feedback
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
    automatic_header_list = SENSOR_STIMULUS[sensor_name]  # Retrieve predefined headers for the sensor
    try:
        # Ask the user if they want to manually select columns for the current sensor
        user_selection = int(
            input(f"Would you like to manually select data columns for '{sensor_name.upper()}' (1)YES/(ENTER)NO: "))
    except ValueError:
        user_selection = 0

    if user_selection:
        # Display available headers for manual selection
        for index, header in enumerate(automatic_header_list):
            print(f'{index}. {header}')
        user_header_selection = input(f"Provide indices to keep for data [0-{index}]: ").split(',')

        # Parse and return the user's selection of headers
        user_header_list = parse_user_selection(user_header_selection, automatic_header_list)
        return user_header_list if user_header_list else automatic_header_list

    # Return the default header list if no manual selection is made
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
        # Handle ranges (e.g., '2-4')
        if '-' in item:
            start, end = map(int, item.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(item))

    # Return the unique list of selected headers within valid index range
    return [header_list[i] for i in sorted(set(indices)) if 0 <= i < len(header_list)]

def gather_data(exports_directory, data_directory):
    """
    Gathers and processes data from sensor directories and organizes the results.

    Args:
        exports_directory (Path): The path to the exports directory where results will be saved.
        data_directory (Path): The path to the data directory containing organized sensor data.

    Returns:
        Path: The path to the results directory where processed data is saved.
    """
    # Create a results directory under the exports directory
    results_directory = create_new_directory(exports_directory / 'Results')

    data_start_indices = {}  # Dictionary to store start indices for each sensor

    # Iterate through each sensor directory in the data directory
    for sensor_directory in data_directory.iterdir():
        sensor_results_dir = create_new_directory(results_directory / sensor_directory.name)
        keep_columns = column_selection(sensor_directory.name)  # Get columns to keep for the sensor

        # Determine the data index for the current sensor
        sensor_files = list(sensor_directory.iterdir())
        data_index = data_index_finder(sensor_directory / sensor_files[0].name)
        data_start_indices[sensor_directory.name] = data_index

        # Process each file in the current sensor directory
        for file in tqdm(sensor_files, desc=f"Processing Files in {sensor_directory.name}"):
            output_path = sensor_results_dir / file.name
            if data_index is not None:
                process_file(file, sensor_results_dir / file.name, keep_columns, data_index)
            else:
                failed_output_path = output_path.parent / f'{file.name}'
                shutil.copy(file, failed_output_path)  # Copy file without processing if index is invalid

    return results_directory

def process_file(file_path, output_path, keep_columns, data_index=0, retry=False):
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
    if retry:
        # Recalculate data index if retrying due to a previous failure
        data_index = data_index_finder(file_path)
        available_columns = pd.read_csv(file_path, skiprows=data_index, nrows=0).columns.tolist()
        keep_columns = [col for col in keep_columns if col in available_columns]

    try:
        # Read the specified columns and save the processed file
        pd.read_csv(file_path, skiprows=data_index, header=0, usecols=keep_columns, low_memory=False).to_csv(
            output_path, index=False)
    except ValueError as error:
        if not retry:
            # Retry processing if not already attempted
            process_file(file_path, output_path, keep_columns, retry=True)
        else:
            print(f"Error: {error}")

# ==========================
# 6. Main Execution Logic
# ==========================
if __name__ == '__main__':
    # Main entry point: Prepare data directories and gather data for processing
    exports_directory, data_directory = prepare_data()
    print(gather_data(exports_directory, data_directory))
