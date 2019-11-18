import argparse
from transfersrc import find_yaml, parser_yaml

parser = argparse.ArgumentParser(description='Run the dlc projects.')
parser.add_argument('--path', metavar='path', type=str, default='analyzed_videos',
                    help='path to project transfer')
args = parser.parse_args()
projectpath = args.path


config_path = find_yaml(wd=projectpath)
print('Importing dlc:')
import deeplabcut as d
print('done')
config = parser_yaml(config_path)
config['project_path'] = projectpath
d.auxiliaryfunctions.write_config(config_path, config)