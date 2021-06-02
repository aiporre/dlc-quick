import yaml
from ruamel.yaml import YAML


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
            enable_last_channel:
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
