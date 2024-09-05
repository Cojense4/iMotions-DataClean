import shutil
import numpy as np
import pandas as pd
from pathlib import Path
import json


# Load the configuration for recognized sensors and stimuli
def load_sensor_config(config_path='SENSORS_config.json'):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['RECOGNIZED_SENSORS'], config['SENSOR_STIMULUS']


RECOGNIZED_SENSORS, SENSOR_STIMULUS = load_sensor_config()


# Helper function to get available directories containing "data" or "results"
def get_directory_by_name(search_directory=Path.home(), keywords=('data', 'results'), max_depth=1):
    def have_dir_access(path):
        """Checks if the program has access to the directory."""
        try:
            # Try listing files in the directory
            for a in path.iterdir():
                return True
        except (PermissionError, NotADirectoryError, FileNotFoundError):
            return False

    def find_directories(directory, depth=0):
        if depth > max_depth:
            return []
        directories = []
        for d in directory.iterdir():
            if have_dir_access(d) and d.is_dir() and 'appdata' not in d.name.lower():                # Check if 'data' or 'results' are in the directory name
                if any(k in d.name.lower() for k in keywords):
                    directories.append(d)

                # Recursively search in subdirectories
                directories.extend(find_directories(d, depth + 1))
        return directories

    dirs = find_directories(search_directory)
    if not dirs:
        print("No directories found.")
        return None

    for i, d in enumerate(dirs, 1):
        print(f"{i}. {d}")

    selected_index = input("Select directory by number: ")
    return dirs[int(selected_index) - 1] if selected_index.isdigit() else dirs[0]


# Get the directory for import and export
def get_import_directory():
    print("Select the import directory:")
    return get_directory_by_name()


def get_export_directory():
    """
    Prompts the user to name their study and select an export directory.

    Returns:
        exports_directory (Path): The created export directory.
    """
    print('-' * 50)

    # Ask the user to input a study name and create an export folder name
    study_name = input("Please name your study: ").strip().replace(" ", "_") or "Study"
    export_folder = f"{study_name}_EXPORTS"

    # Define available directories (Downloads, Desktop, Documents)
    available_directories = [
        Path.home() / "Downloads" / export_folder,
        Path.home() / "Desktop" / export_folder,
        Path.home() / "Documents" / export_folder
    ]

    # Display the available directories to the user
    print("Available EXPORT directories:")
    for index, directory in enumerate(available_directories, start=1):
        print(f"{index}. {directory}")

    # Prompt the user to select a directory by number
    try:
        selected_index = int(input("Use Directory [number]: ")) - 1
        export_directory = available_directories[selected_index]
    except (IndexError, ValueError):
        # Default to the first option if invalid input is provided
        export_directory = available_directories[0]

    return export_directory


# Rename files in sensor directory
def rename_files(sensor_directory, sensor_type):
    for file_path in sensor_directory.iterdir():
        file_name_parts = file_path.stem.split('_')
        new_file_name = f"Survey_{file_name_parts[0]}.csv" if file_name_parts[-1].isalpha() \
            else f"{sensor_type[0]}_{file_name_parts[-1]}.csv"
        file_path.rename(sensor_directory / new_file_name)


# Prepare and organize data in the export directory
def prepare_data():
    import_directory = get_import_directory()
    export_directory = get_export_directory()
    data_directory = export_directory / "Data"

    if data_directory.exists():
        if input("Keep previous data? (yes/no): ").lower() != "yes":
            shutil.rmtree(data_directory, ignore_errors=True)
    shutil.copytree(import_directory, data_directory)

    for sensor_dir in data_directory.iterdir():
        for sensor_type, sensor_names in RECOGNIZED_SENSORS.items():
            if any(sensor.lower() in sensor_dir.name.lower() for sensor in sensor_names):
                sensor_path = data_directory / sensor_type
                sensor_dir.rename(sensor_path)
                rename_files(sensor_path, sensor_type)

    return export_directory


# Detect where the data starts in the file
def data_index_finder(file_path):
    try:
        df = pd.read_csv(file_path, header=None, on_bad_lines='skip', low_memory=False)
        for i, row in df.iterrows():
            first_cell = row[0]
            if first_cell == "#DATA" or first_cell == "sona_id":
                return i + 1
        return None
    except (pd.errors.ParserError, FileNotFoundError):
        print(f"Error reading file: {file_path}")
        return None


# Column selection with user input
def column_selection(sensor_name):
    headers = SENSOR_STIMULUS[sensor_name]
    if input(f"Select columns for '{sensor_name}'? (yes/no): ").lower() == "yes":
        print("\n".join([f"{i}: {h}" for i, h in enumerate(headers)]))
        selected_indices = map(int, input("Select column indices (comma-separated): ").split(','))
        return [headers[i] for i in selected_indices]
    return headers


# Read and process CSV with a fixed number of columns
def read_csv_with_fixed_columns(file_path, num_columns=6):
    df = pd.read_csv(file_path, header=None, on_bad_lines='skip', engine='python')
    if df.shape[1] < num_columns:
        df = df.reindex(columns=range(num_columns), fill_value=np.nan)
    return df.iloc[:, :num_columns]


# Process each file and ensure consistent columns
def process_file(file_path, output_path, keep_columns, data_index, retry=True):
    try:
        df_body = pd.read_csv(file_path, skiprows=data_index, low_memory=False)
        if len(df_body.columns) < 6:
            df_body = read_csv_with_fixed_columns(file_path)

        df_header = pd.read_csv(file_path, nrows=data_index, header=None)
        df_header = df_header.reindex(columns=df_body.columns)  # Adjust header columns

        final_df = pd.concat([df_header, df_body], ignore_index=True)
        final_df.to_csv(output_path, index=False)

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        if retry:
            new_index = data_index_finder(file_path)
            if new_index:
                process_file(file_path, output_path, keep_columns, new_index, retry=False)


# Gather and process data files
def gather_data(export_dir):
    results_dir = Path(export_dir/ "Results")
    results_dir.mkdir(parents=True, exist_ok=True)
    for sensor_dir in (export_dir / "Data").iterdir():
        keep_columns = column_selection(sensor_dir.name)
        for file in sensor_dir.iterdir():
            data_index = data_index_finder(file)
            if data_index is not None:
                process_file(file, results_dir / file.name, keep_columns, data_index)
    return results_dir


# Main execution
if __name__ == '__main__':
    export_directory = prepare_data()
    results_directory = gather_data(export_directory)
    print(f"Data processing complete. Results saved in: {results_directory}")
