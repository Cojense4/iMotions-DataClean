# iMotions Data Cleaner


## Introduction
>***This project is designed to clean iMotions data for further analysis. It's primarily intended for data scientists and researchers who work with iMotions data.***


## Requirements
- This is a **Python** project, uses Python 3.10 <br>
- Required **packages** are found in `requirements.txt`


### Step by Step guide: 
1. Clone the repository:
```bash
git clone https://github.com/Cojense4/iMotions-DataCleaner.git
```
2. Navigate to the project directory:
```bash
cd iMotions-DataCleaner
```
3. Create a virtual environment using **Python 3.10**:
```bash
python -m venv .venv
```
4. Activate the virtual environment:
```bash
# Windows
.venv/Scripts/activate

# Unix or MacOS
source .venv/bin/activate
```

5. Installing required packages: 
```bash 
pip install -r requirements.txt
```

### Data Prepping
- Make sure you have your data stored in a folder titled "Imports" at the root or in the Desktop, Downloads, or Documents<br>
```bash
mkdir test_data && cd test_data
```

- Your data should be split into folders by sensors, and have each participant should be an individual .csv file
```bash
python DataCleaner.py
```  


## Troubleshooting
If data cannot be found to process:

- Is data stored inside `~/Desktop`, `~/Downloads`, or `~/Documents` directory?
- Does your data folder have 'data' in the name? (Ex: 'test_data')?
- Does your data have any of the following sub-directories/data directories?:
    - FACET
    - Shimmer
    - Aurora
    - PolarH10 <br>
    >[!NOTE] <br>
    >These directories should contain participant data exported from iMotions <br>
    >Data directory names have to include the sensor in them (Ex: `~/Desktop/Data/FACET data`)
- Do your data directories have data in them? 


## License
*I will provide the code and data in the repository under an open source license.*<br>
>Copyright 2024, Connor Jensen<br>
>Creative Commons Attribution 4.0 International License (CC BY 4.0)<br>
>http://creativecommons.org/licenses/by/4.0/
