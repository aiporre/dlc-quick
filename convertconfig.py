import argparse
import os
import yaml
from transfersrc import find_yaml, parser_yaml

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--path', metavar='path', type=str, default='TEST-Alex-2019-11-04',
                    help='path to project transfer')
args = parser.parse_args()
projectpath = args.path

def write_config(configname,cfg):
    """
    Write structured config file.
    """
    with open(configname, 'w') as file:
        documents = yaml.dump(cfg, file)
        print(documents)

config_path = find_yaml(wd=projectpath)

config = parser_yaml(config_path)
config['project_path'] = os.path.abspath(projectpath)
print("new path: ",os.path.abspath(projectpath))
new_proj_path = os.path.abspath(projectpath)

# defines a new set of videos with the project path:
video_sets_new = {}
for k,v in config['video_sets'].items():
    video_sets_new[os.path.join(new_proj_path,os.path.basename(k))] = v

config['video_sets']= video_sets_new
write_config(config_path, config)
print(config)