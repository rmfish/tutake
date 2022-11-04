import yaml

from tutake.utils.file_utils import project_root, file

config_file = file(project_root(), 'config.yml')

config = dict()


def asset_required_config(config):
    """
    确认必须的配置项
    :return:
    """


with open(config_file, 'r') as stream:
    config = yaml.safe_load(stream)
    asset_required_config(config)

if __name__ == "__main__":
    print(config['tushare']['tsest']['a'])
