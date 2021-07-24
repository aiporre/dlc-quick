"""

Addaped from:

DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut

Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""


import os
from pathlib import Path

import numpy as np

import deeplabcut.utils
from deeplabcut import auxiliaryfunctions
from deeplabcut.pose_estimation_tensorflow import load_config

def get_snapshots(config_path, shuffle, trainingsetindex=0, modelprefix=""):
    '''
    Read snapshot index from config path and parse actual index. if snapshotindes='all' then it is jused the last one.

    :param config_path: path to the config.yaml of the dlc project. Full path.
    :param shuffle: index of shuffle i.e. training dataset
    :param trainingsetindex: Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).
    :param modelprefix:
    :return:
    '''
    cfg = auxiliaryfunctions.read_config(config_path)
    trainFraction = cfg["TrainingFraction"][trainingsetindex]

    modelfolder = os.path.join(
        cfg["project_path"],
        str(
            auxiliaryfunctions.GetModelFolder(
                trainFraction, shuffle, cfg, modelprefix=modelprefix
            )
        ),
    )
    path_test_config = Path(modelfolder) / "test" / "pose_cfg.yaml"

    try:
        dlc_cfg = load_config(str(path_test_config))
    except FileNotFoundError:
        raise FileNotFoundError(
            "It seems the model for shuffle %s and trainFraction %s does not exist."
            % (shuffle, trainFraction)
        )

    # Check which snapshots are available and sort them by # iterations
    try:
        Snapshots = np.array(
            [
                fn.split(".")[0]
                for fn in os.listdir(os.path.join(modelfolder, "train"))
                if "index" in fn
            ]
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            "Snapshots not found! It seems the dataset for shuffle %s has not been trained/does not exist.\n Please train it before using it to analyze videos.\n Use the function 'train_network' to train the network for shuffle %s."
            % (shuffle, shuffle)
        )
    increasing_indices = np.argsort([int(m.split("-")[1]) for m in Snapshots])
    Snapshots = Snapshots[increasing_indices]
    return Snapshots




def get_snapshot_index(config_path, shuffle, trainingsetindex=0, modelprefix=""):
    '''
    Read snapshot index from config path and parse actual index. if snapshotindes='all' then it is jused the last one.

    :param config_path: path to the config.yaml of the dlc project. Full path.
    :param shuffle: index of shuffle i.e. training dataset
    :param trainingsetindex: Integer specifying which TrainingsetFraction to use. By default the first (note that TrainingFraction is a list in config.yaml).
    :param modelprefix:
    :return:
    '''
    # get all snapshots (eg. [snapshot-3, snapshot-9, ..])
    Snapshots = get_snapshots(config_path, shuffle, trainingsetindex, modelprefix)

    cfg = auxiliaryfunctions.read_config(config_path)
    if cfg["snapshotindex"] == "all":
        print(
            "Snapshotindex is set to 'all' in the config.yaml file. Running video analysis with all snapshots is very costly! Use the function 'evaluate_network' to choose the best the snapshot. For now, changing snapshot index to -1!"
        )
        snapshotindex = -1
    else:
        snapshotindex = cfg["snapshotindex"]

    return Snapshots[snapshotindex]


def find_analyzed_data_generic(folder, videoname, scorer, filtered=False, track_method="", type_file="h5"):
    """Find potential data files from the hints given to the function."""
    scorer_legacy = scorer.replace("DLC", "DeepCut")
    suffix = "_filtered" if filtered else ""
    if track_method == "skeleton":
        tracker = "_sk"
    elif track_method == "box":
        tracker = "_bx"
    elif track_method == "ellipse":
        tracker = "_el"
    else:
        tracker = ""

    candidates = []
    print('+++ >> > >> > > FOLDER:', folder)
    print('========>>>>>>> deeplabcut.utils.grab_files_in_folder(folder, type_file) = ', list(deeplabcut.utils.grab_files_in_folder(folder, type_file)))
    for file in deeplabcut.utils.grab_files_in_folder(folder, type_file):
        if all(
            (
                (
                    file.startswith(videoname + scorer)
                    or file.startswith(videoname + scorer_legacy)
                ),
                "skeleton" not in file,
                (tracker in file if tracker else not ("_sk" in file or "_bx" in file)),
                (filtered and "filtered" in file)
                or (not filtered and "filtered" not in file),
            )
        ):
            candidates.append(file)
    if not len(candidates):
        msg = (
            f'No {"un" if not filtered else ""}filtered data file found in {folder} '
            f"for video {videoname} and scorer {scorer}"
        )
        if track_method:
            msg += f" and {track_method} tracker"
        msg += "."
        raise FileNotFoundError(msg)

    n_candidates = len(candidates)
    if n_candidates > 1:  # This should not be happening anyway...
        print(
            f"{n_candidates} possible data files were found: {candidates}.\n"
            f"Picking the first by default..."
        )
    filepath = os.path.join(folder, candidates[0])
    scorer = scorer if scorer in filepath else scorer_legacy
    return filepath, scorer, suffix
