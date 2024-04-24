import csv
import os
import sys
import shutil
import pandas as pd
import time


def pandas(hidx, start=None, end=None, path=None, R_PATH=None, lbl=False, cols=None):
    """
    The pandas function puts finished files into the results directory, go there after finishing with the data
    The pandas function takes one parameter that are used to objectify the data, it finds the header row by using the
    index value parameter, uses the python engine to parse apart the section, and will feed info back into a spreadsheet

    pandas structure follows as such:
    HEADER: top row, contains names for data, should have timestamps as first column
    LEAD ROW: row before data, contains sona ID in the first cell and the datapoint as the next (ex: Vid0)
    BODY: has the meat of the datapoint data, after the 'StartMedia' row and ends one row before the 'EndMedia' row
    """
    pass


def analyze(r_name=None, r_path=None, g_path=None):  # ex: Desktop\SSAProject\Gather\Raw\R_Aurora.csv
    """
    The analyze function should grab (at this point in the function) the name of the marker, start row for marker,
    and end row for marker
    This function is built as a precursor to the pandas function, it analyzes the gather
    sheet and grabs important data that is needed for pandas()
    """
    pass


def gather():
    """
    The gather function requires two parameters, m_dir (the directory that holds all data, python, etc.)
    <--[Probably not the most secure way to do it lol]
    the other variable is mod, a variable with either "Test" or "Data" depending on whether you are (me) testing the
    program or actually using the full program, (Kellie)

    The gather function structures a report inside the Results directory as such:
    HEADER: -->
    Path=participant path that is used to open in pandas
    SONA=their ID to mark in the result spreadsheet
    Age=how old they are
    Gender=their gender (MALE or FEMALE)
    Start_Row=row index that headers are found on
    [datapoint]=row index the [datapoint] data starts on
    [datapoint]_end=row index the [datapoint] ends on
    BODY: Rows of participants that contain data responding to the header columns

    Patch 1: now code looks for IndexErrors and removes participants who have no data; when code does remove a file,
    it prints the message '{path} removed, no data'
    """
    # New code but testing copilot code to simplify the process
    m_dir = os.getcwd()
    f_user_bool = None
    while f_user_bool not in (0, 1):
        cur_dir_list = [dir_x for dir_x in os.listdir(m_dir) if dir_x[0] != '.']
        for num, x in enumerate(cur_dir_list):
            try:
                f_user_bool = int(input(f'Use "~../{x}" ({num + 1}/{len(cur_dir_list)}) as '
                                        f'import directory? [(0)No/(1)Yes]: '))
            except ValueError:
                f_user_bool = 0
            if bool(f_user_bool) is True:  # Preforms actions if user selects import directory
                f_import_dir = os.path.join(m_dir, x)
                # Have user select where data should end up (Desktop, Documents, Downloads, Other)
                p_dir_dict = {0: 'Desktop', 1: 'Documents', 2: 'Downloads', 3: 'Other'}
                print('Please select where you would like the results to be stored:')
                for key, value in p_dir_dict.items():
                    print(f'\t({key}) {value}')
                try:
                    user_select_dir = int(input('Your selection? '))
                except ValueError:
                    user_select_dir = 0

                if user_select_dir == 0:
                    f_user_dir = os.path.expanduser("~\\Desktop")
                elif user_select_dir == 1:
                    f_user_dir = os.path.expanduser("~\\Documents")
                elif user_select_dir == 2:
                    f_user_dir = os.path.expanduser("~\\Downloads")
                else:
                    f_user_dir = input('Enter directory to use for results: ')
                    f_user_dir = os.path.join(os.path.expanduser("~\\"), f_user_dir)
                    if not os.path.exists(f_user_dir):
                        os.mkdir(f_user_dir)
                m_export_dir = os.path.join(f_user_dir, 'iMotionsData')
                if not os.path.exists(m_export_dir):
                    os.mkdir(m_export_dir)
                f_results_dir = os.path.join(m_export_dir, 'Results')
                if not os.path.exists(f_results_dir):
                    os.mkdir(f_results_dir)
                f_gather_dir = os.path.join(m_export_dir, 'Gather')
                if not os.path.exists(f_gather_dir):
                    os.mkdir(f_gather_dir)
                f_copy_import_dir = os.path.join(m_export_dir, 'Imports')
                if not os.path.exists(f_copy_import_dir):
                    os.mkdir(f_copy_import_dir)
                for file_name in os.listdir(f_import_dir):
                    source = os.path.join(f_import_dir, file_name)
                    destination = os.path.join(f_copy_import_dir, file_name)
                    shutil.copy(source, destination)

                print(f'\nResults Directory: {m_export_dir}')
                return f_import_dir, f_results_dir, f_gather_dir
        return sys.exit('No import directory, exiting...')


if __name__ == '__main__':
    gather()
