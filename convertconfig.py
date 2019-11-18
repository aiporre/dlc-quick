import argparse
import os

from transfersrc import find_yaml, parser_yaml

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--path', metavar='path', type=str, default='TEST-Alex-2019-11-04',
                    help='path to project transfer')
args = parser.parse_args()
projectpath = args.path


config_path = find_yaml(wd=projectpath)
print('Importing dlc:')
import deeplabcut as d
print('done')
config = parser_yaml(config_path)
config['project_path'] = os.path.abspath(projectpath)
print("ppppa: ",os.path.abspath(projectpath))
new_proj_path = os.path.abspath(projectpath)

# defines a new set of videos with the project path:
video_sets_new = {}
for k,v in config['video_sets'].items():
    video_sets_new[os.path.join(new_proj_path,os.path.basename(k))] = v

config['video_sets']= video_sets_new
d.auxiliaryfunctions.write_config(config_path, config)
print(config)