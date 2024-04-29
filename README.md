# iMotions Data Cleaner
## Description
This project is designed to clean iMotions data for further analysis. It's primarily intended for data scientists and researchers who work with iMotions data.


## Features
* prep_data(), stores data in outside directory and creates directories for exports
* clean_data(), preliminarily looks at data and stores keys to data points for cleaning process 
* export_data(), exports cleaned/processed data to export folder 

## Installation
### Prerequisites
Before you begin, ensure you have met the following requirements:
* You have python version >= 3.8 

### Installing iMotion Data Cleaner
To install iMotions Data Cleaner, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/Cojense4/iMotions-DataCleaner.git
```

2. Navigate to the project directory:
```bash
cd iMotions-DataCleaner
```

3. Create a virtual environment:
```bash
python -m venv ./venv
```

4. Activate the virtual environment:
```bash
# Windows
./venv/Scripts/activate

# Unix or MacOS
source venv/bin/activate
```

#### Check venv installation:
to see the files located inside of the virtual environment use the folllowing command:
```bash 
dir ./venv
```
5. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage
### Data Prepping
Make sure you have your data stored in a folder titled "Imports" at the root<br>
```bash
mkdir test_data && cd test_data
```
Your data should be split into folders by sensors, and have each participant should be an individual .csv file
```bash
python DataCleaner.py
```  

## License
*I will provide the code and data in the repository under an open source license.*<br>
>Copyright 2024, Connor Jensen<br>
>Creative Commons Attribution 4.0 International License (CC BY 4.0)<br>
>http://creativecommons.org/licenses/by/4.0/
