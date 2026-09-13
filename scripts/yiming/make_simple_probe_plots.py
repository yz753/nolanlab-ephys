from argparse import ArgumentParser
from pathlib import Path
from common_paths import  eddie_yiming_data_folder, eddie_yiming_deriv_folder
from nolanlab_ephys.probe_info import rec_to_simple_probe, make_probe_plot
from nolanlab_ephys.lab_utils import get_recording_folders, chronologize_paths

parser = ArgumentParser()

parser.add_argument('--mice')
parser.add_argument('--days')
parser.add_argument('--sessions')
parser.add_argument('--data_folder', default=None)
parser.add_argument('--deriv_folder', default=None)

mouse = int(parser.parse_args().mice)
day = int(parser.parse_args().days)

sessions_string = parser.parse_args().sessions
sessions = sessions_string.split(",")

data_folder = parser.parse_args().data_folder
if data_folder is None:
    data_folder = eddie_yiming_data_folder
data_folder = Path(data_folder)

deriv_folder = parser.parse_args().deriv_folder
if deriv_folder is None:
    deriv_folder = eddie_yiming_deriv_folder
deriv_folder = Path(deriv_folder)

recording_paths = chronologize_paths(
        get_recording_folders(data_folder=data_folder, mouse=mouse, day=day, sessions=sessions)
    )

for session, recording_path in zip(
    sessions, recording_paths, strict=True
):
    probe_vector_representation = rec_to_simple_probe(recording_path)
    output_folder = (
        deriv_folder 
        / f"M{mouse:02d}"
        / f"D{day:02d}"
        / session
    )
    output_folder.mkdir(parents=True, exist_ok=True)
    
    make_probe_plot(
        probe_vector_representation, 
        save_path=
        (
            output_folder
            / f"M{mouse:02d}_D{day:02d}_probe_layout.png"
        )
        )
