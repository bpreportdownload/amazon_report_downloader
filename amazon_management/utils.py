import os
import yaml


class YamlConfigLoader(object):
    def __init__(self, config_path):
        if not os.path.isfile(config_path):
            raise ValueError('Could not find configuration file - %s' % config_path)
        self.config_path = config_path

    def load(self):
        with open(self.config_path) as fh:
            config = yaml.load(fh.read(), Loader=yaml.SafeLoader)

        return config
