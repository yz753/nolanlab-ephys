import pandas as pd
from pathlib import Path
from typing import Iterable
from collections import defaultdict
import re

'''This searchs for *ALL* raw ephys recording folders and writes to the yiming_filepaths.csv file.
It also checks if the naming format is correct: M*_D* and days should be continuous, no gap.'''

def search_paths(root: str|Path) -> list[tuple[str, Path]]:
    all_recording_paths = []
    for session in ('VR', 'OF'):
        rel_path = root / 'Yiming/NWR1/ephys/raw' / session
        if not rel_path.is_dir():
            print(f'{session} session folder does not exist.')
            continue
        for path in rel_path.rglob(f"*"):
            if path.is_dir() and (path/'Record Node 101').is_dir():
                all_recording_paths.append((session, path))
    return all_recording_paths
    
    
def check_and_sort_paths(
    recording_paths: Iterable[tuple[str, str | Path]],
    ) -> list[tuple[int, int, str, Path]]:
    format = re.compile(r"^M(\d+)_D(\d+)_(.+)$")
    sorted_dict = defaultdict(set)
    sorted_paths = []
    
    for session, path in recording_paths:
        path = Path(path)
        # check format
        match = format.fullmatch(path.name)
        if match is None:
            print(f'Invalid folder name format: {path.name}.')
            continue
        mouse, day = int(match.group(1)), int(match.group(2))
        
        sorted_dict[mouse].add(day)
        sorted_paths.append((mouse, day, session, path))
        
    # check for gaps in days
    for mouse, days in sorted(sorted_dict.items()):
        first_day, last_day = min(days), max(days)
        # create two sets for days in theory & days observed
        all_days = set(range(first_day, last_day+1))
        gap = sorted(all_days - days)
        
        if gap:
            print(
                f'Discontinuous sessions for mouse M{mouse},'
                f'missing day(s): {", ".join(str(day) for day in gap)}'
            )
            return []
    
    # sort the paths by mouse and day
    sorted_paths.sort(
        key=lambda x: (
            x[0], x[1], x[2], str(x[3])
            )
        )
    return sorted_paths


def write_df(sorted_paths, root):
    return pd.DataFrame(
        [
            {
                'mouse': mouse,
                'day': day,
                'session': session,
                'filepath': str(path.relative_to(root))
            }
            for mouse, day, session, path in sorted_paths
        ]
    )


def main():
    root = Path('/Volumes/INCR-NolanLab/ActiveProjects')
    all_recording_paths = search_paths(root)
    sorted_recording_paths = check_and_sort_paths(all_recording_paths)
    # write to csv
    df = write_df(sorted_recording_paths, root)
    df.to_csv('/Users/zhaoyiming/nolanlab-ephys/scripts/yiming/yiming_filepaths.csv', index=False)
    
    
    
if __name__ == '__main__':
    main()
    