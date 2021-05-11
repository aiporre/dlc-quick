import yaml

def parse_yaml(filepath):
    with open(filepath, 'r') as stream:
        try:
            print('Reading yaml file: ', filepath )
            content = yaml.safe_load(stream)
            print(type(content),'--', content)
            return content
        except yaml.YAMLError as exc:
            print(exc)