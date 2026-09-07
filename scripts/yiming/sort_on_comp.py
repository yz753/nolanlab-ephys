from argparse import ArgumentParser
from pathlib import Path
from nolanlab_ephys.lab_utils import get_recording_folders, chronologize_paths
from nolanlab_ephys.sort import do_sorting_pipeline_concat_then_split
import pandas as pd
from common_paths import local_root, local_yiming_data_folder, local_yiming_deriv_folder, local_yiming_csv_path

import spikeinterface.full as si

def filepath_from_mouse_day_sessions(mouse, day, sessions, path_to_all_filepaths):
    
    all_filepaths = pd.read_csv(path_to_all_filepaths)
    sessions_filepaths = []
    
    for session in sessions:
        session_column = all_filepaths.query(f'mouse == {mouse} & day == {day} & session == "{session}"')
        filepath = session_column['filepath'].values[0]
        sessions_filepaths.append(filepath)

    return sessions_filepaths

def main():

    parser = ArgumentParser()

    parser.add_argument('--mice')
    parser.add_argument('--days')
    parser.add_argument('--sessions')
    parser.add_argument('--protocols')
    parser.add_argument('--data_folder', default=None)
    parser.add_argument('--deriv_folder', default=None)
    parser.add_argument('--filepaths_csv', default=None)

    mice_string = parser.parse_args().mice
    days_string = parser.parse_args().days

    mice = mice_string.split(',')
    mice = [int(mouse) for mouse in mice]

    days = days_string.split(',')
    days = [int(day) for day in days]

    sessions_string = parser.parse_args().sessions
    sessions = sessions_string.split(',')

    protocols_string = parser.parse_args().protocols
    protocols_list = protocols_string.split(',')

    data_folder = parser.parse_args().data_folder
    if data_folder is None:
        data_folder = local_yiming_data_folder
    data_folder = Path(data_folder)

    deriv_folder = parser.parse_args().deriv_folder
    if deriv_folder is None:
        deriv_folder = local_yiming_deriv_folder
    deriv_folder = Path(deriv_folder)
    
    csv_path = parser.parse_args().filepaths_csv
    if csv_path is None:
        csv_path = local_yiming_csv_path
    csv_path = Path(csv_path)

    for mouse in mice:
        for day in days:
        
            mouseday_deriv_folder = deriv_folder / f"M{mouse:02d}/D{day:02d}"
            mouseday_deriv_folder.mkdir(parents=True, exist_ok=True)
        
            recording_paths = filepath_from_mouse_day_sessions(mouse, day, sessions, csv_path)
            
            print(f"\nWill sort the following recordings:")
            for recording_path in recording_paths:
                print(f"  - {recording_path}")
        
            recordings = [si.read_openephys(data_folder / recording_path) for recording_path in recording_paths]
        
            for protocol in protocols_list:
        
                analyzer_paths = [
                    mouseday_deriv_folder / f"{session}/{protocol}/sub-{mouse:02d}_day-{day:02d}_ses-{session}_srt-{protocol}_analyzer"
                    for session in sessions
                ]
        
                do_sorting_pipeline_concat_then_split(
                    recordings,
                    analyzer_paths,
                    protocol,
                    sorting_output_folder=(mouseday_deriv_folder / f"sorting_output_{mouse}_{day}_{protocol}"),
                    n_jobs=8,
                )


if __name__ == "__main__":
    main()
