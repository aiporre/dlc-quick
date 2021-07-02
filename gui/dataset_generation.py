import pandas as pd
import cv2
from deeplabcut.utils import VideoReader
from matplotlib.image import imsave
import os
from random import sample
from gui.utils.video_reading import read_video
from tqdm import tqdm

class VideoReaderArray(VideoReader):
    def __init__(self, video_path):
        super().__init__(video_path=video_path)
        self._current_index = self.video.get(cv2.CAP_PROP_POS_FRAMES)

    def __getitem__(self, index):

        # if not current sets to the target index
        if index != self._current_index:
            current_frame_index = self.video.get(cv2.CAP_PROP_POS_FRAMES)
            # double check here to avoid incorrect reading
            if index != current_frame_index:
                self.set_to_frame(index)
        frame = self.read_frame()
        self._current_index +=1
        return frame



class ContactDataset:
    def __init__(self, labels_path, video_path, dest_path):
        self.labels_path = labels_path
        self.video_path = video_path
        self.dest_path = dest_path
        if not os.path.exists(self.dest_path):
            os.makedirs(dest_path, exist_ok=True)
        if labels_path.endswith('h5'):
            df = pd.read_hdf(labels_path)
            labels_path = labels_path.replace(".h5", ".csv")
            df.to_csv(labels_path)
        self.data = pd.read_csv(labels_path)
        # first extract body parts  nested table
        self.body_parts = self.data.iloc[0].tolist()[1:][::3]
        columns = self.data.columns
        self.column_ids = {}
        pivot = 1
        for b in  self.body_parts:
            self.column_ids[b + '_x'] = columns[pivot]
            self.column_ids[b + '_y'] = columns[pivot + 1]
            self.column_ids[b + '_likelihood'] = columns[pivot + 2]
            pivot += 3

        # reading video frames
        try:
            self.video_frames =  read_video(video_path)
        except MemoryError as e:
            print('ERROR: ' + str(e))
            self.video_frames = VideoReaderArray(video_path)


        # get whisker labels

        # self.whisker_labels = list(set([''.join(i for i in bp if not i.isdigit()) for bp in self.body_parts if bp.startswith('w')]))
        self.whisker_labels = list(set([''.join(i for i in bp if not i.isdigit()) for bp in self.body_parts if bp != 'nose']))
        self.whisker_labels.sort()
        def get_num_items(body_parts, whisker_label):
            print('body parts: ' , body_parts)
            print('whisker label: ', whisker_label)
            return len([ bp for bp in body_parts if bp.startswith(whisker_label) and bp[bp.index(whisker_label)+len(whisker_label)].isdigit()])
        self.whisker_num_items = {wl: get_num_items(self.body_parts, wl) for wl in self.whisker_labels}

    def extract_body_coords(self, body_part):
        data = {}
        for suffix in ['x', 'y', 'likelihood']:
            name = body_part + '_' + suffix
            data[suffix] = self.data[self.column_ids[name]][2:]
        return pd.DataFrame(data).reset_index()

    def get_whisker(self, whisker='b'):
        df_w = None
        for i in range(0, self.whisker_num_items[whisker]):
            wlabel = whisker + str(i)
            df = self.extract_body_coords( wlabel)[["x", "y", "likelihood"]].apply(pd.to_numeric)
            df = df.query('likelihood>0.1')
            df['index'] = df.index.astype(int)
            if df_w is not None:
                df_w = pd.concat([df_w, df], axis=0)
            else:
                df_w = df
        return df_w

    def get_whisker_at(self, whisker_df, n):
        mask = whisker_df.index == n
        #     print('number of whisker at ', n, ' index is ',sum(mask) )
        return whisker_df[mask]

    def capture_positive_frames(self, whisker_label='a'):
        interesting_frames = []
        whisker = self.get_whisker(whisker=whisker_label)
        for i in range(whisker.index.values.max()):
            whisker_at_n = self.get_whisker_at(whisker, i)
            if len(whisker_at_n) >= 5:
                interesting_frames.append(i)
        return interesting_frames

    def capture_negative_frames(self, whisker_label='a'):
        video_length = len(self.video_frames)
        interesting_frames = []
        whisker = self.get_whisker(whisker=whisker_label)
        for i in range(whisker.index.values.max()):
            whisker_at_n = self.get_whisker_at(whisker, i)
            if len(whisker_at_n) >= 5:
                # print('at ', i, ' whisker ', whisker_label, ' has ', len(whisker_at_n))
                interesting_frames.append(i)
        return [j for j in range(video_length) if j not in interesting_frames]

    def generate_dataset(self):
        prefix = os.path.splitext(os.path.basename(self.video_path))[0]

        for whisker_label  in self.whisker_labels:
            # extracting positive frames
            positive_frames = self.capture_positive_frames(whisker_label=whisker_label)
            p_frames = [self.video_frames[i] for i in positive_frames]

            if not os.path.exists(os.path.join(self.dest_path,'positive_frames')):
                os.mkdir(os.path.join(self.dest_path,'positive_frames'))

            if not os.path.exists(os.path.join(self.dest_path, 'negative_frames')):
                os.mkdir(os.path.join(self.dest_path, 'negative_frames'))


            for i, p in tqdm(zip(positive_frames, p_frames), desc=f'Saving Positive frames ({whisker_label}): ', total=len(p_frames)):
                # TODO: image file type is Harcoded!
                imsave(os.path.join(self.dest_path,'positive_frames', prefix + '-w-' + whisker_label +'-f-' + str(i) + '.png'), p)
            # extranting negative frames
            negative_frames = self.capture_negative_frames(whisker_label=whisker_label)
            if len(negative_frames) > len(positive_frames):
                negative_frames = sample(negative_frames, len(positive_frames))

            n_frames = [self.video_frames[i] for i in negative_frames]
            for i, p in tqdm(zip(negative_frames, n_frames), desc=f'Saving Negative frames ({whisker_label}): ', total=len(n_frames)):
                # TODO: image file type is Harcoded!
                imsave(os.path.join(self.dest_path,'negative_frames', prefix + '-w-' + whisker_label +'-f-' + str(i) + '.png'), p)
        print('done')

if __name__ == '__main__':
    labels_path = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/videos/#48_2020-10-25_P3.6_ruleswitch_two_textures_punishrepeat_session03_videos_hispeed2_video_sec45DLC_resnet50_testMay11shuffle1_10.csv'
    video_path = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/videos/#48_2020-10-25_P3.6_ruleswitch_two_textures_punishrepeat_session03_videos_hispeed2_video_sec45.avi'
    dest_path = '/Users/ariel/funana/quick-dlc/test-kunerAG-2021-05-11/training-datasets/iteration-0'

    ContactDataset(labels_path, video_path, dest_path).generate_dataset()