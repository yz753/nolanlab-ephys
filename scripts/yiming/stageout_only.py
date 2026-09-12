from argparse import ArgumentParser
from pathlib import Path

from eddie_helper.make_scripts import run_stage_script
from common_paths import eddie_yiming_deriv_folder, eddie_datastore

parser = ArgumentParser()
parser.add_argument("--mice", required=True)
parser.add_argument("--days", required=True)
parser.add_argument("--sessions", required=True)
parser.add_argument("--protocol", required=True)
args = parser.parse_args()

mice = [int(mouse) for mouse in args.mice.split(",")]
days = [int(day) for day in args.days.split(",")]
sessions = args.sessions.split(",")
protocol = args.protocol

for mouse in mice:
    for day in days:

        dest_folder = (
            eddie_datastore
            / "derivatives"
            / f"M{mouse:02d}"
            / f"D{day:02d}"
        )

        stageout_dict = {}

        for session in sessions:
            source = (
                eddie_yiming_deriv_folder
                / f"M{mouse:02d}"
                / f"D{day:02d}"
                / session
                / protocol
            )

            if not source.exists():
                print(f"Skipping missing source: {source}")
                continue

            stageout_dict[source] = dest_folder / session

        if not stageout_dict:
            print(f"No files to stage out for M{mouse:02d} D{day:02d}")
            continue

        stageout_job_name = f"M{mouse}D{day}stageout"

        run_stage_script(
            stageout_dict,
            job_name=stageout_job_name,
        )