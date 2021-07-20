import argparse
import os, deeplabcut
from pathlib import Path
os.environ['DLClight'] = "True"

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--task', metavar='task', type=str,
                    help='task is the combination of : task-experimenter-date. Example ContrastBW-Ariel-2019-10-10')
parser.add_argument('--video', metavar='video', type=str, default='analyzed_videos',
                    help='video path to video to analyze or directory containing .avi videos (default analyzed_videos)')
parser.add_argument('--train', metavar='train', type=str, default='y', 
                    help='train activation flag (y(default), or n))')
parser.add_argument('--snapshot', metavar='snapshot', type=str, default=None,
                    help='snapshot file to start training (default None, example: snapshot-1000)')
parser.add_argument('--maxiters', metavar='maxiters', type=int, default=10000,
                    help='max number of iterations (default 10000)')
parser.add_argument('--working-dir', metavar='working-dir', type=str, default=None,
                    help='working directory where to find the project')
parser.add_argument('--iteration', metavar='iteration', type=int, default=None,
                    help='Iteration number will select the iteration index \'iteration-0\' for example. Defaults 0')
parser.add_argument('--shuffle', metavar='shuffle', type=int, default=1,
                    help='Shuffle index will select the shuffle to use for creating the training set, train and predict on it. Defaults 1')
parser.add_argument('--training-index', metavar='training-index', type=int, default=0, help='Training index from the config file. Defaults 0')

args = parser.parse_args()

print("Imported DLC!")
print('Configuration selected: ')
print(args)
# finds basepath
task = args.task
if args.working_dir is None:
    basepath=os.path.dirname(os.path.abspath('training.py'))
else:
    basepath = args.working_dir
print('the base path is: ', basepath)

# creates videos list
videoname=args.video
if not os.path.exists(videoname):
    v = os.path.join(basepath,'analyzed_videos',videoname)
    if os.path.exists(v+'.avi') and os.path.isfile(v+'.avi'):
        video=[v+'.avi']
    elif os.path.exists(v) and os.path.isdir(v):
        video = []
        all_videos = list(filter(lambda x: x.endswith('.avi'), os.listdir(v)))
        for vid in all_videos:
            video.append(os.path.join(v, vid))
    else:
        raise FileNotFoundError('File {} not found.'.format(v))
elif os.path.exists(videoname) and os.path.isfile(videoname):
    video = [videoname]
elif os.path.exists(videoname) and os.path.isdir(videoname):
    video = []
    all_videos = list(filter(lambda x: x.endswith('.avi'), os.listdir(videoname)))
    for v in all_videos:
        video.append(os.path.join(videoname, v))
else:
    raise FileNotFoundError('File {} not found.'.format(videoname))

video = [os.path.abspath(v) for v in video]
print('VIDEO PATHH!!!!!!!!!!!!!', video)

# finds config_path
config_path = os.path.join(basepath, task, 'config.yaml')
if not os.path.exists(config_path):
    raise FileNotFoundError("File {} not found. Check that taks and working directory actually contains a project.".format(config_path))
print('config path: ', config_path)

# load project
print('loading demo data... ')
cfg = deeplabcut.auxiliaryfunctions.read_config(config_path)
iteration = cfg['iteration'] if args.iteration is None else args.iteration
shuffle = args.shuffle # default value is 1
training_index = args.training_index # default value sin 0

config_path = Path(config_path).resolve()
config_path = str(config_path)
if cfg.get("multianimalproject", False):
    deeplabcut.create_multianimaltraining_dataset(config_path,num_shuffles=shuffle, Shuffles=[shuffle],)
else:
    deeplabcut.create_training_dataset(config_path, num_shuffles=shuffle, Shuffles=[shuffle])

# training network
print('training network... ')
if args.snapshot is not None:
    train_path=os.path.join(cfg['project_path'],
                          'dlc-models',
                          'iteration-'+str(iteration),
                          cfg['Task'] + cfg['date'] + '-trainset' + str(int(cfg['TrainingFraction'][training_index] * 100)) + 'shuffle' + str(shuffle),
                          'train')
    train_path = os.path.abspath(train_path)
    posefile = os.path.join(train_path,'pose_cfg.yaml')
    print('pose file : ', posefile)
    DLC_config=deeplabcut.auxiliaryfunctions.read_plainconfig(posefile)
    DLC_config['init_weights'] = args.snapshot #os.path.join(train_path,args.snapshot)
    deeplabcut.auxiliaryfunctions.write_plainconfig(posefile,DLC_config)


if args.train == 'y':
    deeplabcut.train_network(config_path, shuffle=shuffle, displayiters=2, saveiters=100, maxiters=args.maxiters)
print('training done.')

# analyzing video
print('analizing videos: ', video)
deeplabcut.analyze_videos(config_path, shuffle=shuffle, trainingsetindex=training_index, videos=video, save_as_csv=True, videotype='.avi')

# create outputs
print('generating labeled video')
deeplabcut.create_labeled_video(config_path, video)
print('generating plots')
deeplabcut.plot_trajectories(config_path, video)
