from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from gui.utils.parse_yaml import extractTrainingIndexShuffle, parse_yaml
from gui.dataset_generation import ContactDataset, OscilationDataset
from gui.utils.snapshot_index import get_snapshot_index
from whisker_utils.predictor import PredictorBase
from whisker_utils.video_utils import VideoIterator
import os
import pandas as pd


class OscDLCPredictor(PredictorBase):
    CLASSES = ['No Oscillation', 'Oscillation']

    def __init__(self, experiments_path, selections=None, animals=None, dates=None, codes=None, sessions=None,
                 cameras=None, config_path=None):
        super(OscDLCPredictor, self).__init__(experiments_path, selections=selections, animals=animals, dates=dates,
                                                  codes=codes, sessions=sessions, cameras=cameras)
        # generate model
        assert config_path is not None, "config must be given."
        self.config_path = config_path
        self.gputouse = None
        cfg = parse_yaml(self.config_path)
        iteration_path = os.path.join(cfg['project_path'], "dlc-models", "iteration-" + str(cfg['iteration']))
        self.contact_config_path = os.path.join(iteration_path, "osc-model", "osc.yaml")
        cfg_contact = parse_yaml(self.contact_config_path)
        self.shuffle = cfg_contact.get('shuffle', None)
        if self.shuffle is None:
            shuffle_files = [f for f in os.listdir(iteration_path) if "shuffle" in f]
            self.shuffle = shuffle_files[-1]
        self.train_index, self.shuffle_number = extractTrainingIndexShuffle(self.config_path, self.shuffle)
        self.make_dlc_osc_pred = cfg_contact.get("make_dlc_pred", False)
        self.track_method = cfg_contact.get("track_method", "ellipse")

    def make_prediction(self, force_recalculation=False):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        import deeplabcut as d
        # setting the path to the dataset:
        cfg = parse_yaml(self.config_path)
        training_fraction = cfg["TrainingFraction"][self.train_index]
        scorer, _ = d.utils.GetScorerName(cfg, self.shuffle_number, training_fraction)
        _projsuffix = self.shuffle.split('-')[0]  # project name and date
        scorer = scorer[:scorer.index(_projsuffix)]
        # get the snapshot number at the end of the string
        snapshot_string = get_snapshot_index(self.config_path,
                                             shuffle=self.shuffle_number,
                                             trainingsetindex=self.train_index)
        snapshot_number = snapshot_string.split('-')[-1]

        label_ending = f'{scorer}{_projsuffix}shuffle{self.shuffle_number}_{snapshot_number}'

        for is_proc, video in tqdm(zip(self.processed, self.videos), total=len(self.videos), desc=f'Processing videos: {dt_string}'):
            if not is_proc and not force_recalculation:
                sec = video.name.split('_')[-1].split('.')[0]
                # TODO: for more prediction the saving of the results is outside this method. So search Results instead
                fname, _ = os.path.splitext(video.resolve().absolute())

                time_table_path = fname + ".csv"
                if not os.path.exists(time_table_path):
                    time_table_path = os.path.join(video.parent, 'video_' + sec + '_timestamps.csv')
                results = pd.read_csv(time_table_path, sep=';') if os.path.exists(time_table_path) else None
                video_iter = VideoIterator(video)

                d.analyze_videos(self.config_path,
                                 videos=[str(video)],
                                 shuffle=self.shuffle_number,
                                 trainingsetindex=self.train_index,
                                 gputouse=self.gputouse,  # fill out directly choose first
                                 save_as_csv=True,
                                 destfolder=None)
                identity_only = cfg.get('identity', False)
                d.convert_detections2tracklets(self.config_path, videos=[str(video)],
                                               shuffle=self.shuffle_number,
                                               trainingsetindex=self.train_index,
                                               track_method=self.track_method,
                                               overwrite=True,
                                               identity_only=identity_only,
                                               destfolder=None)
                try:
                    d.stitch_tracklets(self.config_path,
                                       videos=[str(video)],
                                       shuffle=self.shuffle,
                                       trainingsetindex=self.train_index,
                                       n_tracks=None,
                                       track_method=self.track_method,
                                       destfolder=None)
                except Exception:
                    print("Failed to extract tracklets to video: ", video)
                    continue
                if self.make_dlc_osc_pred and results is not None:
                    label_path = os.path.splitext(video)[0] + label_ending + ".h5"
                    contact_dataset = OscilationDataset(labels_path=label_path, video_path= video,
                                                        dest_path=str(Path(video).parent))
                    preds, angles_r, angles_l = contact_dataset.estimateOscilation()
                    labels = list(map(lambda x: self.CLASSES[0] if x else self.CLASSES[1], preds))
                    if len(preds) != len(video_iter):
                        print(
                            f'\033[0;33m Failed to read video {video.resolve().absolute()}. Please check and maybe delete or replace it manually.\033[0m')
                        continue

                    # merging predictions and saving:
                    # TODO: deal with second time, i.e. columns already exist
                    results['dlc_whisker_osc'] = preds
                    results['dlc_label_osc'] = labels
                    results['dlc_angles_right'] = angles_r
                    results['dlc_angles_left'] = angles_l

                    # write results
                    results.to_csv(fname + ".csv", sep=';')
                    results.to_hdf(fname + ".h5", 'contact_model_table')


class ContactDLCPredictor(PredictorBase):
    CLASSES = ['No Contact', 'Contact']

    def __init__(self, experiments_path, selections=None, animals=None, dates=None, codes=None, sessions=None,
                 cameras=None, config_path=None):
        super(ContactDLCPredictor, self).__init__(experiments_path, selections=selections, animals=animals, dates=dates,
                                                  codes=codes, sessions=sessions, cameras=cameras)

        # generate model
        assert config_path is not None, "config must be given."
        self.config_path = config_path
        self.gputouse = None
        cfg = parse_yaml(self.config_path)
        iteration_path = os.path.join(cfg['project_path'], "dlc-models", "iteration-" + str(cfg['iteration']))
        self.contact_config_path = os.path.join(iteration_path, "contact-model", "contact.yaml")
        cfg_contact = parse_yaml(self.contact_config_path)
        self.shuffle = cfg_contact.get('shuffle', None)
        if self.shuffle is None:
            shuffle_files = [f for f in os.listdir(iteration_path) if "shuffle" in f]
            self.shuffle = shuffle_files[-1]
        self.trainindex, self.shuffle_number = extractTrainingIndexShuffle(self.config_path, self.shuffle)
        self.make_dlc_contact_pred = cfg_contact.get("make_dlc_pred", False)

    def make_prediction(self, force_recalculation=False):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        import deeplabcut as d
        # setting the path to the dataset:
        cfg = parse_yaml(self.config_path)
        training_fraction = cfg["TrainingFraction"][self.trainindex]
        scorer, _ = d.utils.GetScorerName(cfg, self.shuffle_number, training_fraction)
        _projsuffix = self.shuffle.split('-')[0]  # project name and date
        scorer = scorer[:scorer.index(_projsuffix)]
        # get the snapshot number at the end of the string
        snapshot_string = get_snapshot_index(self.config_path,
                                             shuffle=self.shuffle_number,
                                             trainingsetindex=self.trainindex)
        snapshot_number = snapshot_string.split('-')[-1]

        label_ending = f'{scorer}{_projsuffix}shuffle{self.shuffle_number}_{snapshot_number}'

        for is_proc, video in tqdm(zip(self.processed, self.videos), total=len(self.videos), desc=f'Processing videos: {dt_string}'):
            if not is_proc and not force_recalculation:
                sec = video.name.split('_')[-1].split('.')[0]
                # TODO: for more prediction the saving of the results is outside this method. So search Results instead
                fname, _ = os.path.splitext(video.resolve().absolute())

                time_table_path = fname + ".csv"
                if not os.path.exists(time_table_path):
                    time_table_path = os.path.join(video.parent, 'video_' + sec + '_timestamps.csv')
                results = pd.read_csv(time_table_path, sep=';') if os.path.exists(time_table_path) else None
                video_iter = VideoIterator(video)

                d.analyze_videos(self.config_path,
                                 videos=[str(video)],
                                 shuffle=self.shuffle_number,
                                 trainingsetindex=self.trainindex,
                                 gputouse=self.gputouse, # fill out directly choose first
                                 save_as_csv=True,
                                 destfolder=None)
                if self.make_dlc_contact_pred and results is not None:
                    label_path = os.path.splitext(video)[0] + label_ending + ".h5"
                    contact_dataset = ContactDataset(labels_path=label_path,video_path= video, dest_path=str(Path(video).parent))
                    preds, contacts = contact_dataset.estimate_contacts()
                    labels = list(map(lambda x: self.CLASSES[0] if x else self.CLASSES[1], contacts))
                    if len(preds) != len(video_iter):
                        print(
                            f'\033[0;33m Failed to read video {video.resolve().absolute()}. Please check and maybe delete or replace it manually.\033[0m')
                        continue

                    # merging predictions and saving:
                    # TODO: deal with second time, i.e. columns already exist
                    results['dlc_whisker_contact'] = preds
                    results['dlc_label_contact'] = labels

                    # write results
                    results.to_csv(fname + ".csv", sep=';')
                    results.to_hdf(fname + ".h5", 'contact_model_table')


if __name__ == '__main__':
    experiments_path = r"Z:\Ariel\datasets\behavior_whisker_data_test"
    predictor = ContactDLCPredictor(experiments_path, config_path=r"Z:\Ariel\models\dlc\wcontact4-agkuner-2020-12-03\config.yaml")
    # print(predictor.videos)
    predictor.make_prediction()
