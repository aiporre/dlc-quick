import pandas as pd
import cv2
from deeplabcut.utils import VideoReader
from matplotlib.image import imsave
import os
from random import sample
from gui.utils.video_reading import read_video
from tqdm import tqdm
import numpy as np
from scipy.signal import butter, sosfilt, spectrogram
from librosa import power_to_db
import hashlib

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

def write_video(filepath, shape, fps=30):
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    video_height, video_width, CHANNELS = shape
    video_filename = filepath
    writer = cv2.VideoWriter(video_filename, fourcc, fps, (video_width, video_height), isColor=True)
    return writer

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype='band', output='sos')
    return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfilt(sos, data)
    return y

class OscilationDataset:
    def __init__(self, labels_path, video_path, dest_path):
        self.labels_path = labels_path
        self.video_path = video_path
        self.dest_path = dest_path
        vname = os.path.basename(self.video_path)
        hash_object = hashlib.md5(vname.encode())
        self.vname_hash = hash_object.hexdigest()
        # read data frame from labels
        self.data = pd.read_hdf(self.labels_path)
        # create destination directory if doesn't exists
        if not os.path.exists(os.path.join(self.dest_path, 'positive')):
            os.makedirs(os.path.join(self.dest_path, 'positive'), exist_ok=True)
        if not os.path.exists(os.path.join(self.dest_path, 'negative')):
            os.makedirs(os.path.join(self.dest_path, 'negative'), exist_ok=True)
        self.bodyparts = self.data.columns.get_level_values(2).unique().values
        self.scorer = self.data.columns.get_level_values(0).unique().values[0]
        self.individuals = self.data.columns.get_level_values(1).unique().values

    def extract_body_coords(self, individual, bodypart):
        scorer = self.data.columns.get_level_values(0).unique().values[0]
        return self.data[scorer, individual, bodypart]

    # get dataframe of whisker (multindex dataframe)
    def get_whisker(self, whisker='wR1'):
        scorer = self.data.columns.get_level_values(0).unique().values[0]
        df_w = self.data[scorer, whisker]
        return df_w

    # get coordinates at given time n from a whisker dataframe
    def get_whisker_at(self, whisker_df, n):
        return whisker_df.iloc[n]

    # get the coordinates of the nose
    def get_nose(self):
        label = 'nose'
        df_nose = self.extract_body_coords('single', label)[["x", "y", "likelihood"]].apply(pd.to_numeric)
        df_nose = df_nose.query('likelihood>0.9')
        df_nose['index'] = df_nose.index.astype(int)
        return df_nose

    # calculate angles:
    def calculate_angles(self, whisker, nose, pos_target='a1'):
        all_angles = []
        for i, nose_values in nose.iterrows():
            n = int(nose_values['index'])
            whisker_n = self.get_whisker_at(whisker, n)
            base_vec = None
            if not np.isnan(whisker_n['b0', 'x']) and not np.isnan(whisker_n['b0', 'y']):
                base_vec = np.array([whisker_n['b0', 'x'] - nose_values['x'], whisker_n['b0', 'y'] - nose_values['y']])
                base_vec = base_vec / max(1E-5, np.linalg.norm(base_vec))
            whisker_vec = None

            if base_vec is not None and \
                    not np.isnan(whisker_n[pos_target, 'x']) and \
                    not np.isnan(whisker_n[pos_target, 'y']):
                whisker_vec = np.array([whisker_n[pos_target, 'x'] - base_vec[0],
                                        whisker_n[pos_target, 'y'] - base_vec[1]])
                whisker_vec = whisker_vec / max(1E-5, np.linalg.norm(whisker_vec))

            if base_vec is not None and whisker_vec is not None:
                prods = whisker_vec.dot(base_vec)
                angles = 180.0 * np.arccos(prods) / np.pi
                all_angles.append({'n': n, 'angles': angles})
            else:
                all_angles.append({'n': n, 'angles': np.nan})
        return all_angles

    def calculate_angles_side(self, side='R'):
        df_angles = None
        individuals = [f'w{side}{i}' for i in range(1, 5)]
        whisker_pos = [bp for bp in self.bodyparts if bp.startswith('a')]
        nose = self.get_nose()
        for ind in individuals:
            w = self.get_whisker(whisker=ind)  # whisker='wR1'
            for aa in whisker_pos:
                angles = self.calculate_angles(w, nose, pos_target=aa)
                a = pd.DataFrame(angles)
                a.index = a.n
                a = a.drop(columns=['n'])
                ranges = a['angles'].max() - a['angles'].min()
                #     print(ranges)
                asdf = (a['angles'] - a['angles'].min()).div(ranges)
                #     print(asdf)
                a['angles_' + ind + '_' + aa] = asdf
                a = a.drop(columns=['angles'])
                if df_angles is None:
                    df_angles = a
                else:
                    df_angles = pd.concat([df_angles, a], axis=1)
        return df_angles

    # this function resumes the process to get oscilation windows that will be used actually in analysis
    def get_oscilation_windows(self, df_angles, fs):
        mean_angle = df_angles.mean(axis=1).interpolate().dropna(axis=0)
        x = mean_angle.values
        # filtering
        lowcut = 3.0  # Hz
        highcut = 15.0  # hz
        t = mean_angle.index / fs
        y = butter_bandpass_filter(x, lowcut, highcut, fs, order=9)
        y = y * (x > 0)
        # stft

        nperseg = fs // 4
        noverlap = nperseg // 4
        freqs, times, Sxx = spectrogram(y, fs, window=('tukey', 0.5),
                                        nperseg=nperseg, noverlap=noverlap)
        Sxx_db = power_to_db(Sxx, ref=Sxx.max())
        # window selection criteria
        window_times = []
        offset = mean_angle.index.min()
        for i, tt in enumerate(times):
            sxx = Sxx_db[:, i]
            whisking_range = (freqs < 15) * (freqs > 3)
            not_whisking_range = ~(whisking_range)
            if sxx[whisking_range].max() > -3.5 and sxx[whisking_range].max() - 2.49 > sxx[not_whisking_range].mean():
                window_times.append([offset / fs + tt - 0.125,
                                     offset / fs + tt + 0.125,
                                     offset + i * nperseg,
                                     offset + min((i + 1) * nperseg, len(y))])
        return window_times, freqs, times, Sxx_db

    def generate_dataset(self, fs=240, slow_motion=False):
        df_angles_r = self.calculate_angles_side(side='R')
        df_angles_l = self.calculate_angles_side(side='L')
        windows_r, freqs_r, times_r, Sxx_db_r = self.get_oscilation_windows(df_angles_r, fs=fs)
        windows_l, freqs_l, times_l, Sxx_db_l = self.get_oscilation_windows(df_angles_l, fs=fs)
        windows = windows_r + windows_l
        # unique windows
        windows_unique = []
        # traverse for all elements
        for x in windows:
            # check if exists in unique_list or not
            if x not in windows_unique:
                windows_unique.append(x)
        # make a vid array
        vid = VideoReaderArray(self.video_path)
        print('metadata : ', vid.metadata)
        print('length robust: ', vid.get_n_frames(robust=True))
        H, W, C = vid[0].shape
        fps_out = 30 if slow_motion else fs
        # generates positive videos
        video_counter = 0
        for t0, t1, index0, index1 in windows_unique:
            positive_frames = list(range(index0, index1))
            clip_vname = f'whisker_clip_{self.vname_hash}_{video_counter}.avi'
            print('creating clip: ', clip_vname)
            clip_video_path = os.path.join(self.dest_path, 'positive', clip_vname)
            print('path to clip: ', clip_video_path, 'frames ', len(positive_frames), 'shape ', (H, W, C))
            writer = write_video(clip_video_path, (H, W, C), fps=fps_out)
            for i in positive_frames:
                writer.write(vid[i].astype('uint8'))
            writer.release()
            video_counter += 1
            vid_clip = read_video(clip_video_path)
            clip_data = {'data': vid_clip,
                         'spectrogram_r': [freqs_r, times_r, Sxx_db_r],
                         'spectrogram_l': [freqs_l, times_l, Sxx_db_l],
                         't0': t0,
                         't1': t1,
                         'index0':index0,
                         'index1': index1,
                         'window_time': t1-t0,
                         'window_index': index1-index0,
                         'video_name': os.path.basename(self.video_path)}
            np.save(clip_video_path.replace('.avi', '.npy'), clip_data)


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