import os
import pandas as pd
from old_DataCleaner import *
from pathlib import Path


def getData(path):
    timeTook = 0
    questionsCorrect = 0
    questions = 0
    sonaId = pd.read_csv(path, nrows=0, skiprows=0).columns.values[1]
    restOfData = pd.read_csv(path, skiprows=1,header=0,usecols=[0,4,5])

    for index, row in restOfData.iterrows():
        questions += 1
        if row.to_list()[1]:
            questionsCorrect += 1
        timeTook += row.to_list()[2]
        

    return [sonaId, f'{questionsCorrect/questions:.2f}', timeTook]



def cleaner():
    homeDirectory = os.path.expanduser('~')
    FBLDataDirectory = os.path.join(homeDirectory, 'Desktop')
    FBLDataDirectory = os.path.join(FBLDataDirectory, 'fblmist_results')
    resultsDirectory = createNewDirectory(os.path.join(FBLDataDirectory, 'RESULT'))
    resultsPath = os.path.join(resultsDirectory, 'RESULT.csv')
    resultsData = []

    for file in Path(FBLDataDirectory).iterdir():
        if file.name.endswith('.csv'):
            resultsData.append(getData(file))
    surveyResults = pd.DataFrame(resultsData, columns=['SONA ID', '% Correct', 'Leftover Time'])
    surveyResults.to_csv(resultsPath)


if __name__ == "__main__":
    cleaner()