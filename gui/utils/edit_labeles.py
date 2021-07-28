from gui.utils.parse_yaml import parse_yaml
import deeplabcut as dlc
import os
import pandas as pd
import shutil
import argparse

class Labels:
    def __init__(self, config, video):
        self.config = config
        self.video = video
        self.cfg = parse_yaml(self.config)
        self.labels_path = os.path.join(self.cfg['project_path'], 'labeled-data', video)
        self.scorer = self.cfg["scorer"]
        (
            self.individual_names,
            self.uniquebodyparts,
            self.multibodyparts,
        ) = dlc.utils.auxfun_multianimal.extractindividualsandbodyparts(self.cfg)
        self.dataFrame = pd.read_hdf(
            os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".h5")
        )
        # Handle data previously labeled on a different platform
        sep = "/" if "/" in self.dataFrame.index[0] else "\\"
        if sep != os.path.sep:
            self.dataFrame.index = self.dataFrame.index.str.replace(
                sep, os.path.sep
            )
        self.dataFrame.sort_index(inplace=True)

    def get_individuals(self):
        cfg = parse_yaml(self.config)
        return cfg['individuals']


    def remove_individual(self, indiviual):
        self.dataFrame.drop([(self.scorer,indiviual)], axis=1, inplace=True)
        self.individual_names = list(filter(lambda x: x != indiviual, self.individual_names))

    def save(self):
        # checks backup
        if not os.path.exists(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.csv")):
            shutil.copy2(os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".csv"),
                         os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.csv"))
        if not os.path.exists(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.h5")):
            shutil.copy2(os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".h5"),
                         os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.h5"))
        # Windows compatible
        self.dataFrame.sort_index(inplace=True)
        print("INDIVIDUALS: ", self.dataFrame.columns.get_level_values("individuals"))
        print('self individuals: ', self.individual_names)
        # Discard data associated with bodyparts that are no longer in the config
        config_bpts = self.cfg["multianimalbodyparts"] + self.cfg["uniquebodyparts"]
        valid = [
            bp in config_bpts
            for bp in self.dataFrame.columns.get_level_values("bodyparts")
        ]
        self.dataFrame = self.dataFrame.loc[:, valid]
        # Re-organize the dataframe so the CSV looks consistent with the config
        self.dataFrame = self.dataFrame.reindex(
            columns=self.individual_names, level="individuals"
        ).reindex(columns=config_bpts, level="bodyparts")
        self.dataFrame.to_csv(
            os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".csv")
        )
        self.dataFrame.to_hdf(
            os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".h5"),
            "df_with_missing",
            format="table",
            mode="w",
        )
        print("__>> INDIVIDUALS: ", self.dataFrame.columns.get_level_values("individuals"))
        print('__>> self individuals: ', self.individual_names)

    def rollback(self):
        if os.path.exists(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.csv")):
            shutil.copy2(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.csv"),
                         os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".csv"))
        if os.path.exists(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.h5")):
            shutil.copy2(os.path.join(self.labels_path, "CollectedData_" + self.scorer + "_original.h5"),
                         os.path.join(self.labels_path, "CollectedData_" + self.scorer + ".h5"))



def edit_labels(config, video=None, remove=False, individuals=None, rollback=False):
    cfg = parse_yaml("/Users/ariel/funana/projects-whisker/wtfree5ma-agkuner-2021-06-25/config.yaml")
    if video is None:
        print('editing all videos')
        videos = cfg['video_sets'].keys()
        for video in videos:
            vname = os.path.splitext(os.path.basename(video))[0]
            try:
                labels = Labels(config, vname)
            except Exception as e:
                # print('reror: ', e)
                continue
            print('editing: video: ', vname)
            if remove:
                for inv in individuals:
                    labels.remove_individual(inv)
                labels.save()
            if rollback:
                labels.rollback()

    else:
        print('editing video: ', video)
        labels = Labels(config, video)
        if remove:
            for inv in individuals:
                labels.remove_individual(inv)
            labels.save()
        if rollback:
            labels.rollback()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Edit labels.')
    parser.add_argument('config', metavar='path to config.yaml', type=str,
                        help='path to the config.yaml')
    parser.add_argument('--video', metavar='video', type=str, default=None,
                        help='video path to video to analyze or directory containing .avi videos (default analyzed_videos)')
    parser.add_argument('--remove', action='store_true',
                        help='Remove individual?')
    parser.add_argument('--individuals', metavar='snapshot', type=str, nargs='+', default=None,
                        help='list of individuals to delete')
    parser.add_argument('--rollback', action='store_true',
                        help='rollback labels?')
    args = parser.parse_args()

    edit_labels(config=args.config, video=args.video, remove=args.remove, individuals=args.individuals,rollback=args.rollback)







