import os
import sys


def rename():
    """Goes back one repository and goes to ../Imports"""
    m_dir = '\\'.join(os.getcwd().split('\\')[0:-1])
    m_dir = os.path.join(m_dir, 'Imports')
    for analysis in os.listdir(m_dir):
        f_dir = os.path.join(m_dir, analysis)
        for sensor in os.listdir(f_dir):
            s_dir = os.path.join(f_dir, sensor)
            for file in os.listdir(s_dir):
                print(file)
                sys.exit()


if __name__ == '__main__':
    rename()
