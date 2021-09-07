import os

import yaml


def get_videos(videosList):
    count = videosList.GetItemCount()
    videos = []
    for row in range(count):
        item = videosList.GetItem(itemIdx=row, col=1)
        videos.append(item.GetText())
    return videos


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
    if not len(config_yamls) == 0:
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
            print('Reading yaml file: ', filepath)
            content = yaml.safe_load(stream)
            print(type(content), '--', content)
            return content
        except yaml.YAMLError as exc:
            print(exc)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_available_gpus():
    from tensorflow.python.client import device_lib
    local_device_protos = device_lib.list_local_devices()
    gpus_strings = [x.name for x in local_device_protos if x.device_type == 'GPU']
    def get_last_number(gpu_string):
        tokens = [s for s in gpu_string.split(':') if s.isdigit()]
        return tokens[-1]
    return [get_last_number(gpu) for gpu in gpus_strings]


def get_radiobutton_status(radiobuttons):
    status = {}
    for k in radiobuttons.keys():
        status[k] = radiobuttons[k].GetValue()

    if status['All']:
        return 'all'
    else:
        return [k for k, v in status.items() if v and not k == 'All']