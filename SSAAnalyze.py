import csv
import os
import sys
import pandas as pd
import time


def dir_get(mode):
    m_dir = os.getcwd()
    if mode == 'i':
        dir_bool = None
        while dir_bool not in (0, 1):
            for num, x in enumerate(os.listdir(m_dir)):
                try:
                    dir_bool = int(input(f'Use "~..\\{x}" ({num + 1}/{len(os.listdir(m_dir))}) as '
                                         f'import directory? [(0)No/(1)Yes]: '))
                except ValueError:
                    dir_bool = 0
                if bool(dir_bool) is True:
                    i_path = os.path.join(m_dir, x)
                    return i_path
    elif mode == 'r':
        select_dir = {1: 'Desktop', 2: 'Documents', 3: 'Downloads', 4: 'Other'}
        print('Please select where you would like the final data to be stored:')
        for key, value in select_dir.items():
            print(f'\t({key}) {value}')
        user_dir_selection = input('Your selection? ')
        print(user_dir_selection)
        """
        r_dir = os.path.join(m_dir, 'Results')
        if not os.path.exists(r_dir):
            try:
                dir_bool = int(input(f'Create results directory at {r_dir}? [(1)Yes/(0)No]: '))
            except ValueError:
                dir_bool = 1
            if bool(dir_bool) is True:
                os.mkdir(r_dir)
            else:
                sys.exit('No results directory, exiting...')
        return r_dir
    elif mode == 'g' or mode == 'r':
        e_dir = os.path.join(m_dir, 'Exports')
        if not os.path.exists(e_dir):
            try:
                dir_bool = int(input(f'Create export directory at {e_dir}? [(1)Yes/(0)No]: '))
            except ValueError:
                dir_bool = 1
            if bool(dir_bool) is True:
                os.mkdir(e_dir)
            else:
                sys.exit('No export directory, exiting...')
        if mode == 'r':
            r_dir = os.path.join(e_dir, 'Results')
            if not os.path.exists(r_dir):
                os.mkdir(r_dir)
            return r_dir
        else:
            g_dir = os.path.join(e_dir, 'Gather')
            if not os.path.exists(g_dir):
                os.mkdir(g_dir)
        return g_dir
    """

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
    if lbl is True:
        col_labels = pd.read_csv(path, header=(hidx - 1), nrows=0, usecols=cols)
        col_labels = col_labels.drop('SourceStimuliName', axis=1)
        col_labels.to_csv(R_PATH, mode='w+', index=False)
    data = pd.read_csv(path, nrows=(end - (start - 1)), skiprows=(start - 1), header=None, usecols=cols)
    with open(R_PATH, 'a') as res:
        res_writer = csv.writer(res, lineterminator='\n')
        sona_label = [path.split('\\')[-1][2:-4], data[7][0]]
        res_writer.writerow(sona_label)
    data = data.drop(7, axis=1)
    data = data.drop(0, axis=0)
    data.dropna().to_csv(R_PATH, mode='a', header=False, index=False)


def analyze(r_name=None, r_path=None, g_path=None):  # ex: Desktop\SSAProject\Gather\Raw\R_Aurora.csv
    """
    The analyze function should grab (at this point in the function) the name of the marker, start row for marker,
    and end row for marker
    This function is built as a precursor to the pandas function, it analyzes the gather
    sheet and grabs important data that is needed for pandas()
    """
    use_cols = [1, 7]
    if r_name == 'Raw_Aurora.csv' or r_name == 'Tasks_Aurora.csv':
        use_cols2 = [9, 10, 11, 12, 13]
        use_cols += use_cols2
    elif r_name == 'Raw_Shimmer.csv' or r_name == 'Raw_Facet.csv' or r_name == 'Tasks_Facet.csv':
        use_cols2 = [9, 10, 11]
        use_cols += use_cols2
    with open(g_path, 'r') as gtr:
        label = True
        gtr_reader = csv.reader(gtr)
        for line in gtr_reader:
            if gtr_reader.line_num >= 2:
                for cell_index in range(len(line)):
                    if cell_index == 0:
                        p_path = line[cell_index]
                    if cell_index == 4:
                        h_idx = int(line[cell_index])
                    elif cell_index >= 5:
                        if (cell_index - 3) % 3 == 0:
                            start_idx = int(line[cell_index]) + h_idx
                        elif (cell_index - 4) % 3 == 0:
                            end_idx = int(line[cell_index]) + h_idx
                            if label is False:
                                pandas(hidx=h_idx, start=start_idx, end=end_idx, path=p_path,
                                       R_PATH=r_path, cols=use_cols)
                            else:
                                pandas(hidx=h_idx, start=start_idx, end=end_idx, path=p_path,
                                       R_PATH=r_path, lbl=label, cols=use_cols)
                                label = False


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
    i_dir = dir_get('i')                            # Import directory
    print(i_dir)
    g_dir = dir_get('g')                            # Gather directory
    print(g_dir)
    r_dir = dir_get('r')                            # Results directory
    print(r_dir)
    s_time = time.time()                            # Start time
    print(s_time)
    """
    for num0, analysis in enumerate(os.listdir(i_dir)):
        a_start = time.time()
        print(f'Gathering {analysis} data...')
        a_dir = os.path.join(i_dir, analysis)       # Analysis directory
        for num1, sensor in enumerate(os.listdir(a_dir)):
            g_name = f'gtr_{analysis[0]}{sensor}.csv'
            g_path = os.path.join(g_dir, g_name)    # Gather csv path
            s_dir = os.path.join(a_dir, sensor)     # Sensor directory
            gtr_columns = ['Path', 'SONA', 'Age', 'Gender', 'Start_Row']
            if analysis == 'Raw':
                for num_r in range(1, 13):
                    if num_r == 1:
                        gtr_columns.append(f'JG_1226')
                        gtr_columns.append(f'JG_1226-lo_denim_resize')
                        gtr_columns.append(f'JG_1226_end')
                    elif num_r == 2:
                        gtr_columns.append(f'JS_0744')
                        gtr_columns.append(f'JS_0744-lo_denim_resize')
                        gtr_columns.append(f'JS_0744_end')
                    elif num_r == 3:
                        gtr_columns.append(f'MR1_0132')
                        gtr_columns.append(f'MR1_0132-lo_denim_resize')
                        gtr_columns.append(f'MR1_0132_end')
                    elif num_r == 4:
                        gtr_columns.append(f'PM')
                        gtr_columns.append(f'PupilMeasure_dot')
                        gtr_columns.append(f'PM_end')
                    elif num_r <= 6:
                        gtr_columns.append(f'PM{num_r - 4}')
                        gtr_columns.append(f'PupilMeasure_dot-{num_r - 4}')
                        gtr_columns.append(f'PM{num_r - 4}_end')
                    elif num_r <= 9:
                        gtr_columns.append(f'SAM{num_r - 7}')
                        gtr_columns.append(f'SAM Two Dimensions{num_r - 7}')
                        gtr_columns.append(f'SAM{num_r - 7}_end')
                    elif num_r <= 11:
                        gtr_columns.append(f'V{num_r - 10}')
                        gtr_columns.append(f'Vid{num_r - 10}')
                        gtr_columns.append(f'V{num_r - 10}_end')
                    elif num_r == 12:
                        gtr_columns.append(f'V2')
                        gtr_columns.append(f'Vid2 with Alarm')
                        gtr_columns.append(f'V2_end')
            elif analysis == 'Tasks':
                for num_t in range(1, 6):
                    if num_t < 3:
                        gtr_columns.append(f'OCQ{num_t}')
                        gtr_columns.append(f'Overconfidence Questions{num_t}')
                        gtr_columns.append(f'OCQ{num_t}_end')
                    elif num_t == 3:
                        gtr_columns.append(f'Qual2')
                        gtr_columns.append(f'Qualtrics-2')
                        gtr_columns.append(f'Qual2_end')
                    else:
                        gtr_columns.append(f'RQ{num_t - 3}')
                        gtr_columns.append(f'Risk Question {num_t - 3}')
                        gtr_columns.append(f'RQ{num_t - 3}_end')
            else:
                sys.exit(f'Not set up for gathering {analysis} data yet')
            with open(g_path, 'w+', newline='') as gtr:
                gtr_writer = csv.writer(gtr)
                gtr_writer.writerow(gtr_columns)
                for num2, participant in enumerate(os.listdir(s_dir)):
                    old_path = os.path.join(s_dir, participant)
                    new_path = os.path.join(s_dir, f'{sensor[0]}_{participant[-9:]}')
                    if not os.path.isfile(new_path):
                        os.rename(old_path, new_path)
                        print(f'File renamed to ...{new_path[-12:]}')
                    p_path = new_path
                    with open(p_path, 'r') as p_data:
                        part_reader = csv.reader(p_data)
                        p_row = list()              # Participant's gather data row container
                        row_sections = list()       # Participant's marker section holder
                        for line in part_reader:
                            if line[0] == '#Respondent Name':
                                p_row.append(p_path)
                                p_row.append(line[1])
                            elif line[0] == '#Respondent Age':
                                p_row.append(line[1])
                            elif line[0] == '#Respondent Gender':
                                p_row.append(line[1])
                            elif line[0] == 'Row':
                                p_row.append(part_reader.line_num)
                                try:
                                    if line[8] == '':
                                        pass
                                except IndexError:
                                    p_data.close()
                                    os.remove(p_path)
                                    print(f'{p_path} removed, no data')
                                    break
                            elif line[3] == 'StartMedia':
                                row_section = [line[7], int(line[0])]  # Marker name, marker start row
                            elif line[3] == 'EndMedia':
                                row_section.append(int(line[0]))    # End Row
                                row_sections.append(row_section)    # Append to row sections list as layered list
                        row_sections.sort(key=lambda x: x[0])
                        for section in row_sections:
                            for data in section:
                                p_row.append(data)
                    gtr_writer.writerow(p_row)
            print(f'Analyzing {analysis}-{sensor} data...')
            r_name = f'{analysis}_{sensor}.csv'       # Raw_Aurora.csv
            r_path = os.path.join(r_dir, r_name)
            analyze(r_name=r_name, r_path=r_path, g_path=g_path)
        print(f'Finished {analysis} processing in {time.time() - a_start:.1f} seconds\n')
    print(f'Total time: {time.time() - s_time:.1f} seconds!')
"""


if __name__ == '__main__':
    gather()
    input('enter anything to quit: ')
