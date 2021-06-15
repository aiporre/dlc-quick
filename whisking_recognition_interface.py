import PySimpleGUI as sg
import os
from pathlib import Path
from datetime import datetime

from options.options import OptionInterface


def main():
    # data_dir = sg.popup_get_folder('Select a folter to process:')
    data_dir = '/Volumes/GG2/behavior_whisker_data'
    assert Path(data_dir).name.startswith('behavior_whisker_data'), 'folder data naming convesion is not correct. Must be named as : "behavior_whisker_data...(something)"'
    # extract animals
    animals = os.listdir(data_dir)
    # extract dates
    dates = []
    def is_date(ele):
        try:
            datetime.strptime(ele, "%Y-%m-%d")
            return True
        except:
            return False
    for animal in animals:
        print(os.listdir(os.path.join(data_dir, animal)))
        dates.extend(filter(is_date, os.listdir(os.path.join(data_dir, animal))))
    dates = list(set(dates))

    # sessions and codes
    sessions = []
    codes = []
    for session_path in Path(data_dir).glob('*/*/*'):
        if 'session' in session_path.name:
            session = session_path.name.split('_')[-1]
            sessions.append(session)
            codes.append(session_path.name[:session_path.name.index(session)-1])
    sessions = list(set(sessions))
    codes = list(set(codes))

    # sorting stuff:
    animals.sort(), codes.sort(), dates.sort(), sessions.sort()


    # print stuff:

    print('ANIMALS')
    print(animals)
    print('DATES')
    print(dates)
    print('CODES')
    print(codes)
    print('SESSIONS')
    print(sessions)

    # ask which....
    def ask_which(options_text, status=0):
        options_status = [status]*len(options_text)
        opt_interface = OptionInterface(options_text, options_status)
        opt_interface.launch()
        new_options_text = []
        for o, s in zip(opt_interface.options_text, opt_interface.options_status):
            print(f'OPTION ({o}) => {s}')
            if s in [1,3]:
                new_options_text.append(o)
        return new_options_text
   
    # 1. which animal?
    animals = ask_which(animals)
    if len(animals) == 0:
        return

    # 1. which animal?
    dates = ask_which(dates)
    if len(dates) == 0:
        return

    # 1. which animal?
    codes = ask_which(codes)
    if len(codes) == 0:
        return

    # 1. which animal?
    sessions = ask_which(sessions)
    if len(sessions) == 0:
        return

    # 1. which animal?
    cameras = [os.path.join('videos','hispeed1'), os.path.join('videos','hispeed2')]
    cameras = ask_which(cameras)
    if len(cameras) == 0:
        return

    # print more stuff
    print('NEW ANIMALS')
    print(animals)
    print('NEW DATES')
    print(dates)
    print('NEW CODES')
    print(codes)
    print('NEW SESSIONS')
    print(sessions)
    print('NEW cameras')
    print(cameras)

    # last check all options:
    all_options = []
    for a in animals:
        for d in dates:
            for c in codes:
                for s in sessions:
                    for cam in cameras:
                        pp = os.path.join(a, d, c, s, cam)
                        if os.path.exists(pp):
                            all_options.append(pp)
    all_options = ask_which(all_options)


    a = input("Do you want to refine?  [Y/n]")
    while a.lower() in ["y",'yes','no','n']:
        a = input("Do you want to refine? [Y/n] (write Y, yes, n or no)")
    if a.lower() in ['Yes', 'y']:
        all_options = ask_which(all_options)

    print(all_options)
if __name__ == '__main__':
    main()


