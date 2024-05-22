from pathlib import Path
import os
import sys
import shutil
import pandas as pd

RECOGNIZED_SENSORS = {
    'FACET': ['Camera', 'Emotient', 'FACET'],
    'Shimmer': ['Shimmer', 'GSR'],
    'Aurora': ['Eyetracker', 'Smart Eye', 'Aurora'],
    'PolarH10': ['Bluetooth Low Energy', 'Polar H10', 'HeartRate']
}

SENSOR_STIMULUS = {
    'FACET': ['Timestamp','SlideEvent','SourceStimuliName','SampleNumber', 'Timestamp RAW', 'Timestamp CAL', 'System Timestamp CAL', 'VSenseBatt RAW',
              'VSenseBatt CAL', 'Internal ADC A13 PPG RAW', 'Internal ADC A13 PPG CAL', 'GSR RAW' , 'GSR Resistance CAL',
              'GSR Conductance CAL', 'Heart Rate PPG ALG', 'IBI PPG ALG', 'Packet reception rate RAW'],
    'Shimmer': ['Timestamp','SlideEvent','SourceStimuliName','SampleNumber','Timestamp RAW','Timestamp CAL','System Timestamp CAL','VSenseBatt RAW','VSenseBatt CAL',
                'Internal ADC A13 PPG RAW','Internal ADC A13 PPG CAL','GSR RAW', 'GSR Resistance CAL',
                'GSR Conductance CAL','Heart Rate PPG ALG','IBI PPG ALG','Packet reception rate RAW'],
    'Aurora': ['Timestamp','SlideEvent','SourceStimuliName','ET_GazeLeftx','ET_GazeLefty','ET_GazeRightx','ET_GazeRighty','ET_PupilLeft','ET_PupilRight',
               'ET_TimeSignal','ET_DistanceLeft','ET_DistanceRight','ET_CameraLeftX','ET_CameraLeftY','ET_CameraRightX',
               'ET_CameraRightY','ET_Distance3D','ET_HeadRotationPitch','ET_HeadRotationYaw','ET_HeadRotationRoll',
               'ET_GazeDirectionLeftQuality','ET_GazeDirectionRightQuality','ET_EyelidOpeningLeft',
               'ET_EyelidOpeningLeftQuality','ET_EyelidOpeningRight','ET_EyelidOpeningRightQuality',
               'ET_LeftPupilDiameterQuality','ET_RightPupilDiameterQuality'],
    'PolarH10': ['Timestamp','SlideEvent','SourceStimuliName','Heart rate','R-R interval','Energy expended','Contact'],
}

def createNewDirectory(newPath):
    if not os.path.exists(newPath):
        try:
            os.makedirs(newPath)
        except OSError as error:
            sys.exit(f"Failed to create directory: {error}")
    return newPath


def prepareData():
    """
    Prepares the data for cleaning and analysis.

    This function prompts the user to select an import directory and a directory to store the results.
    It creates the necessary directories and copies the data from the import directory to the export directory.
    It also renames the files based on the recognized sensors.

    Returns:
        activeDirectories (dict): A dictionary containing the paths to the results directory, gather directory, and data directory.
    """
    def overwriteDirectory(directory):
        try:
            removePreviousData = bool(int(input("Do you want to delete the previous data? (0)NO/(1)YES: ")))
        except:
            return overwriteDirectory(directory)
        if removePreviousData:
            shutil.rmtree(directory)
            shutil.copytree(importDirectory, directory)
    
    def renameDirectory(directory):
        for sensorType, sensorName in RECOGNIZED_SENSORS.items():
            if any(sensorKeyword in directory.name for sensorKeyword in sensorName):
                newDirectory = Path(os.path.join(dataDirectory, sensorType))
                directory.rename(newDirectory)
                for fileName in newDirectory.iterdir():
                    name, ext = fileName.stem, fileName.suffix
                    name = name.split('_')[-1]
                    newFileName = f"{sensorType[0]}_{name}{ext}"
                    fileName.rename(newDirectory / newFileName)
                break
        else:
            print(f'Warning: ({directory.name}) not recognized or already created')

    def getImportDirectory():
        availableDirectories = list()
        for directory in Path.cwd().iterdir():
            if directory.is_dir() and directory.name.find('data') >= 0:
                availableDirectories.append(directory)

        print('-'*50)
        print("Available IMPORT directories:")
        for index, directory in enumerate(availableDirectories, start=0):
            print(f"{index}. {directory}")
        try:
            userDirectory = int(input("Use Directory [number]: "))
            importDirectory = availableDirectories[userDirectory]
        except:
            return getImportDirectory()
        return importDirectory 

    def createDataDirectory():
        print('-'*50)
        print("Available EXPORT directories:")
        print(f'0. {Path.home() / "Downloads" / "iMotions_Exports"}')
        print(f'1. {Path.home() / "Desktop" / "iMotions_Exports"}')
        print(f'2. {Path.home() / "Documents" / "iMotions_Exports"}')
        try:
            userExportDirectory = int(input("Choose Directory: "))
        except:
            return createDataDirectory()
        else:
            if userExportDirectory == 0:
                exportsDirectory = createNewDirectory(Path.home() / "Downloads" / "iMotions_Exports")
            elif userExportDirectory == 1:    
                exportsDirectory = createNewDirectory(Path.home() / "Desktop" / "iMotions_Exports")
            elif userExportDirectory == 2:
                exportsDirectory = createNewDirectory(Path.home() / "Documents" / "iMotions_Exports")
            else:
                return createDataDirectory()
        dataDirectory = createNewDirectory(os.path.join(exportsDirectory, 'Data'))
        return Path(exportsDirectory), Path(dataDirectory)
    
    importDirectory = getImportDirectory()
    exportsDirectory, dataDirectory = createDataDirectory()
    overwriteDirectory(dataDirectory)
    userSensors = [x for x in dataDirectory.iterdir() if x.is_dir()] 
    for sensorPath in userSensors:
        renameDirectory(sensorPath)
    return exportsDirectory, dataDirectory


def gatherData(exportsDirectory, dataDirectory):
    """
    Gets rid of unwanted data selected by user.

    This function prompts the user to indecies for columns of data they would like to keep. 
    The program then uses pandas to efficiently grab that data and exports it to the 'results' directory created by the prepareData() function

    Returns:
        activeDirectories['results']: A path object to the results directory.
    """
    def dataIndexFinder(filePath):
        INDEXMAX = 40
        INDEXSTART = 19
        dataStartIndex = 19

        firstCellData = pd.read_csv(filePath, nrows=1, skiprows=INDEXSTART).iloc[0,0]
        while firstCellData != '#DATA':
            if dataStartIndex >= INDEXMAX:
                print("Error: Could not find the end of the header rows.")
                return INDEXSTART
            dataStartIndex += 1
            firstCellData = pd.read_csv(filePath, nrows=1, skiprows=dataStartIndex).iloc[0,0]            
        return dataStartIndex + 2
    
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

    resultsDirectory = createNewDirectory(os.path.join(exportsDirectory, 'Results'))
    for sensorName in os.listdir(dataDirectory):
        currentResultsDirectory = createNewDirectory(os.path.join(resultsDirectory, sensorName))
        currentDataDirectory = os.path.join(dataDirectory, sensorName)
        keepColumns = columnSelection(sensorName)
        for fileName in os.listdir(currentDataDirectory):
            fileResultsPath = os.path.join(currentResultsDirectory, fileName)
            fileDataPath = os.path.join(currentDataDirectory, fileName)
            fileDataIndex = dataIndexFinder(fileDataPath)
            
            try:
                dataframe = pd.read_csv(fileDataPath, skiprows=fileDataIndex, header=0, usecols=keepColumns, low_memory=False)
            except ValueError as error:
                errorColumns = str(error).split(': ')[1]
                errorKeepColumns = [col for col in keepColumns if col not in errorColumns]
                dataframe = pd.read_csv(fileDataPath, skiprows=fileDataIndex, header=0, usecols=errorKeepColumns, low_memory=False)
            finally:
                dataframe.to_csv(fileResultsPath)
    return 
    #TODO: Utilize df headers for files to get metadata (find place to put metadata)
    #TODO: Finish this section of the code, should be finding a way to smartly detect which columns to keep based on the data


if __name__ == '__main__':
    exportsDirectory, dataDirectory = prepareData()
    results_dir = gatherData(exportsDirectory, dataDirectory)
    #TODO: Turn this program into an application for easier user experience
