import csv
import os
import sys
import shutil
import pandas as pd
import time


def export_data(hidx, start=None, end=None, path=None, R_PATH=None, lbl=False, cols=None):
    pass


def clean_data(r_name=None, r_path=None, g_path=None):
    pass


def gather_data(m_dir, mod=None):
    pass


def prep_data():
    m_dir = os.getcwd()
    f_user_bool = None
    while f_user_bool not in (0, 1):
        cur_dir_list = [dir_x for dir_x in os.listdir(m_dir) if dir_x[0] != '.' and os.path.isdir(os.path.join(m_dir, dir_x))]
        for num, x in enumerate(cur_dir_list):
            try:
                f_user_bool = int(input(f'Use "~../{x}" ({num + 1}/{len(cur_dir_list)}) as '
                                        f'import directory? [(0)No/(1)Yes]: '))
            except ValueError:
                f_user_bool = 0
            if bool(f_user_bool) is True:
                f_import_dir = os.path.join(m_dir, x)
                print(f_import_dir)
                p_dir_dict = {0: 'Desktop', 1: 'Documents', 2: 'Downloads', 3: 'Other'}
                print('Please select where you would like the results to be stored:')
                for key, value in p_dir_dict.items():
                    print(f'\t({key}) {value}')
                try:
                    user_select_dir = int(input('Your selection? '))
                except ValueError:
                    user_select_dir = 0
                if user_select_dir == 0:
                    f_user_dir = os.path.join(os.path.expanduser("~"), "Desktop")
                elif user_select_dir == 1:
                    f_user_dir = os.path.join(os.path.expanduser("~"), "Documents")
                elif user_select_dir == 2:
                    f_user_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                else:
                    f_user_dir = input('Enter directory to use for results: ')
                    f_user_dir = os.path.join(os.path.expanduser("~"), f_user_dir)
                if not os.path.exists(f_user_dir):
                    os.mkdir(f_user_dir)
                m_export_dir = os.path.join(f_user_dir, 'iMotionsData')
                if os.path.exists(m_export_dir):
                    shutil.rmtree(m_export_dir)
                os.mkdir(m_export_dir)
                f_results_dir = os.path.join(m_export_dir, 'Results')
                os.mkdir(f_results_dir)
                f_gather_dir = os.path.join(m_export_dir, 'Gather')
                os.mkdir(f_gather_dir)
                f_copy_import_dir = os.path.join(m_export_dir, 'test_data')
                shutil.copytree(f_import_dir, f_copy_import_dir)

                print(f'\nResults Directory: {m_export_dir}')
                return m_export_dir
    return sys.exit('No import directory, exiting...')

if __name__ == '__main__':
    export_dir = prep_data()
    gather_data(export_dir)