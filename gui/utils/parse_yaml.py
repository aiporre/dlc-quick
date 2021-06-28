import yaml
from ruamel.yaml import YAML
from numpy import round, array

def parse_yaml(filepath):
    with open(filepath, 'r') as stream:
        try:
            print('Reading yaml file: ', filepath )
            content = yaml.safe_load(stream)
            print(type(content),'--', content)
            return content
        except yaml.YAMLError as exc:
            print(exc)
def create_whisking_config_template():
    yaml_str = """\
    # Dataset parameters
            datapath:
            enable_eager:
            image_dim_width:
            image_dim_height:
            \n
    # Dataset optimization
            cache:
            shuffle_buffer:
            split_rate:
            \n
    # Training parameters
            learning_rate:
            display_iter:
            batch_size:
            init_weights:
            """
    ruamelFile = YAML()
    cfg_file = ruamelFile.load(yaml_str)

    return cfg_file, ruamelFile


def write_whisking_config(configname, cfg):

    with open(configname, "w") as cf:
        cfg_file, ruamelFile = create_whisking_config_template()

        for key in cfg.keys():
            cfg_file[key] = cfg[key]

        ruamelFile.dump(cfg_file, cf)


def extractTrainingIndexShuffle(config, pose_config_parent):
    '''
    parse the shuffle and training index from the parent dir name of pose config

    :param config: path to the config file
    :param pose_config_parent: example 'trainset41shuffle1'
    :return:
    '''
    token = pose_config_parent.split('-')[-1]
    trainingFraction = int(token[len('trainset'): len('trainset')+2])
    shuffle = int(token[token.index('shuffle')+len('shuffle'):])
    cfg = parse_yaml(config)
    trainingFactionsConfig = cfg['TrainingFraction']
    # THIS IS PATCH FOR A BUG IN DLC, parsing the text is the only thing this function should do, but now is fixing the config.yaml
    # trainingIndex = (trainingFactionsConfig-round(trainingIndex/100,2)).argmin()
    trainingIndex = None
    computedFraction = round(trainingFraction / 100, 2)
    for i, tf in enumerate(trainingFactionsConfig):
        if computedFraction == tf:
            trainingIndex = i
    if trainingIndex is None:
        import deeplabcut as dlc
        trainingIndex = len(trainingFactionsConfig)
        trainingFactionsConfig.append(computedFraction)
        dlc.auxiliaryfunctions.write_config(config, {'TrainingFraction': trainingFactionsConfig})

    return trainingIndex, shuffle

