import logging
import os.path
from pathlib import Path

import yaml

from tutake.utils.file_utils import project_root

logger = logging.getLogger("tutake.config")


class DotConfig(dict):

    def __getattr__(self, k):
        try:
            v = self[k]
            if isinstance(v, dict):
                return DotConfig(v)
            return v
        except KeyError:
            return None

    def __getitem__(self, k):
        try:
            if isinstance(k, str) and '.' in k:
                k = k.split('.')
            if isinstance(k, (list, tuple)):
                def loop(v, kk):
                    try:
                        if len(kk) == 1 and isinstance(v, dict):
                            return v[kk[0]]
                        if isinstance(v, dict):
                            return loop(v[kk[0]], kk[1:])
                        return None
                    except KeyError or TypeError or BaseException:
                        return None

                return loop(self, k)
            return super().__getitem__(k)
        except KeyError or TypeError or BaseException:
            return None

    def get(self, k, default=None):
        try:
            v = self[k]
            if v is None:
                return default
            return v
            # if isinstance(k, str) and '.' in k:
            #     return self[k]
            # return super().get(k, default=default)
        except KeyError or TypeError:
            return default

    def set(self, key, val):
        def __set(_c, k, v):
            if isinstance(k, str) and '.' in k:
                k = k.split('.')
            if isinstance(k, (list, tuple)):
                item = _c.get(k[0])
                if item is None:
                    item = {}
                    _c[k[0]] = item
                if isinstance(item, dict):
                    k_list = k[1:]
                    if len(k_list) == 1:
                        k_list = k_list[0]
                    return __set(item, k_list, v)
                else:
                    return False
            _c[k] = v
            return True

        return __set(self, key, val)


TUTAKE_SQLITE_DRIVER_URL_KEY = "tutake.data.driver_url"
TUSHARE_TOKEN_KEY = "tushare.token"
DEFAULT_TUSHARE_TOKEN = "4907b8834a0cecb6af0613e29bf71847206c41ddc3e598b9a25a0203"  # 网上随机找的，兜底程序一定可用
TUSHARE_API_META_DIR_KEY = "tushare.meta.driver_url"
TUSHARE_DIR_KEY = "tutake.dir"


class TutakeConfig(object):

    def __init__(self, path):
        self.__config = self._load_config_file('{}/config.yml'.format(path))
        self._default_config()

    def _default_config(self):
        """
        确认必须的配置项
        :return:
        """
        data_driver_url = self.get_config(TUTAKE_SQLITE_DRIVER_URL_KEY)
        meta_driver_url = self.get_config(TUSHARE_API_META_DIR_KEY)
        self.set_tutake_dir(self.get_config(TUSHARE_DIR_KEY))

        if data_driver_url:
            self.set_config(TUTAKE_SQLITE_DRIVER_URL_KEY, data_driver_url)
        if meta_driver_url:
            self.set_config(TUSHARE_API_META_DIR_KEY, meta_driver_url)

        if self.get_config(TUSHARE_TOKEN_KEY) is None:
            self.set_config(TUSHARE_TOKEN_KEY, DEFAULT_TUSHARE_TOKEN)

        logger.debug("Set default config. {}", self.__config)

    def _load_config_file(self, config_file: str) -> DotConfig:
        if os.path.exists(config_file):
            with open(config_file, 'r') as stream:
                return DotConfig(yaml.safe_load(stream))
        else:
            logger.error("Config file is not exits. %s" % config_file)
        return DotConfig()

    def merge_config(self, _config: dict):
        if _config is not None:
            for key in _config:
                self.set_config(key, _config[key])

    def require_config(self, key: str):
        config = self.get_config(key)
        if config is None:
            raise Exception("Missing required config with key %s" % key)
        return config

    def get_config(self, key: str, default_val=None):
        if key is not None:
            val = self.__config.get(key)
            if val is None:
                return default_val
            else:
                return val
        else:
            return default_val

    def set_config(self, key, val) -> True:
        return self.__config.set(key, val)

    def set_tutake_dir(self, tutake_dir: str = None):
        def _get_default_driver_url(path, dir):
            if path is None:
                path = "%s/.tutake" % Path.home()
            driver_url = 'sqlite:///%s/%s' % (path, dir)
            return driver_url

        tutake_driver_url = _get_default_driver_url(tutake_dir, 'data')
        logger.info("Set config %s %s" % (TUTAKE_SQLITE_DRIVER_URL_KEY, tutake_driver_url))
        self.set_config(TUTAKE_SQLITE_DRIVER_URL_KEY, tutake_driver_url)
        tutake_driver_url = _get_default_driver_url(tutake_dir, 'meta')
        logger.info("Set config %s %s" % (TUSHARE_API_META_DIR_KEY, tutake_driver_url))
        self.set_config(TUSHARE_API_META_DIR_KEY, tutake_driver_url)

    @staticmethod
    def __set(config: DotConfig, k, v):
        return config.set(k, v)

    def get_data_sqlite_driver_url(self):
        return self.require_config(TUTAKE_SQLITE_DRIVER_URL_KEY)

    def get_meta_sqlite_driver_url(self):
        return self.require_config(TUSHARE_API_META_DIR_KEY)

    def set_tushare_token(self, tushare_token):
        self.set_config(TUSHARE_TOKEN_KEY, tushare_token)

    def get_tushare_token(self):
        return self.require_config(TUSHARE_TOKEN_KEY)


tutake_config = TutakeConfig(project_root())
