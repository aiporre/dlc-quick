import os
import yaml

def find_yaml(wd=None):
    '''
    Find the most likely yaml config file in the current directory
    wd:working directory to search for the yaml
    :return:
    '''
    config_yamls = []
    yamls = []
    cwd = os.getcwd() if wd is None else wd
    for dirpath, dnames, fnames in os.walk(cwd):
        for f in fnames:
            if f.endswith("config.yaml"):
                config_yamls.append(os.path.join(dirpath, f))
            elif f.endswith(".yaml"):
                yamls.append(os.path.join(dirpath, f))
    print('Yaml options found:', yamls, ' or configs: ', config_yamls)
    config_yaml = ''
    if not len(config_yamls)==0:
        config_yaml = config_yamls[-1]
    elif len(config_yamls) == 0 and not len(yamls) == 0:
        config_yaml = yamls[-1]
    else:
        print('no config yaml found using empty string')
        config_yaml = ''
    print('using : ', config_yaml)
    return config_yaml


def parser_yaml(filepath):
    with open(filepath, 'r') as stream:
        try:
            print('Reading yaml file: ', filepath )
            content = yaml.safe_load(stream)
            print(type(content),'--', content)
            return content
        except yaml.YAMLError as exc:
            print(exc)