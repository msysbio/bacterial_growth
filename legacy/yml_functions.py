import yaml

yaml.Dumper.ignore_aliases = lambda self, data: True

def read_yml(file):
    """
    A function to read yml file

    :param file: yml

    :return info (if ok)
    """
    try:
        with open(file) as f:
            info = yaml.safe_load(f)
        return info
    except yaml.YAMLError as exc:
        print('\n\tERROR: Check your YAML file, maybe you used forbidden characters (i.e., :)\n')
        exit()
