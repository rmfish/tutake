import logging
import yaml
import logging.config
import os


def setup_logging(default_path='../../ts_logger.yml', default_level=logging.DEBUG):
    path = default_path
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level, force=False)


if __name__ == '__main__':
    yaml_path = 'ts_logger.yml'
    setup_logging()
    # logging.debug('Start')
    logger = logging.getLogger("api")
    logger.debug("api debug")
