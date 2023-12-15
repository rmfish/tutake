import logging
import os.path
import pickle
from os.path import dirname, abspath, join
from pathlib import Path

import yaml

from tutake.utils.logger import setup_logging
from tutake.utils.utils import project_root, file_dir, realpath


class DotConfig(dict):

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        self.update(state)

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


TUTAKE_TEST_MODE = "tutake.test_mode"
TUTAKE_DRIVER_URL_KEY = "tutake.data.driver_url"
TUTAKE_DATA_DIR_KEY = "tutake.data.dir"
TUTAKE_REMOTE_SERVER_KEY = "tutake.remote.address"
TUTAKE_SERVER_PORT_KEY = "tutake.server.port"
TUSHARE_TOKEN_KEY = "tushare.token"
TUSHARE_TOKEN_CHECK_KEY = "tushare.token_check"
TUSHARE_TOKENS_KEY = "tushare.tokens"
DEFAULT_TUSHARE_TOKEN = "4907b8834a0cecb6af0613e29bf71847206c41ddc3e598b9a25a0203"  # 网上随机找的，兜底程序一定可用
TUSHARE_META_DRIVER_URL_KEY = "tushare.meta.driver_url"
TUSHARE_META_DIR_KEY = "tushare.meta.dir"
TUTAKE_PROCESS_THREAD_CNT_KEY = 'tutake.process.thread_cnt'
TUTAKE_LOGGING_CONFIG_KEY = 'tutake.logger.config_file'
TUTAKE_SCHEDULER_CONFIG_KEY = 'tutake.scheduler'
TUTAKE_SQLITE_TIMEOUT_CONFIG_KEY = 'tutake.sqlite.timeout'
TUTAKE_PROCESS_FORBIDDEN_CONFIG_KEY = 'tutake.process.forbidden'
TUTAKE_DATABASE_TYPE = 'duckdb'


class TutakeConfig(object):

    def __init__(self, absolute_config_path=None):
        self.empty = False
        _config_path = absolute_config_path
        if absolute_config_path is not None and os.path.isdir(absolute_config_path):
            _config_path = Path(f'{absolute_config_path}/config.yml')
        if absolute_config_path is None or not os.path.exists(_config_path):
            _config_path = Path(f'{project_root()}/config.yml')
            if not os.path.exists(_config_path):
                print(f"Tutake config file [{absolute_config_path}] is not exists. use empty config.")
                self.empty = True
            else:
                print(
                    f"Tutake config file [{absolute_config_path}] is not exists. use the default configfile. {_config_path}")
        self.config_file = _config_path
        self.__config = self._load_config_file(self.config_file)
        self._default_config()
        self._remote_client = None
        self._tutake = None

    def __setstate__(self, state):
        self.__config = state.get('config')
        self.config_file = state.get('config_file')
        self._default_config()

    def __getstate__(self):
        return {'config_file': self.config_file, "config": self.__config}

    def load_tutake(self):
        if self._tutake is not None:
            return self._tutake
        else:
            from tutake import Tutake
            self._tutake = Tutake(self.config_file)
            return self._tutake

    def _default_config(self):
        """
        确认必须的配置项
        :return:
        """
        data_dir = Path(realpath(self.get_config(TUTAKE_DATA_DIR_KEY) or self._get_default_data_dir('database')))
        if not data_dir.exists():
            data_dir.mkdir(parents=True)
            # os.makedirs(data_dir)
        self.set_tutake_data_dir(data_dir)

        meta_dir = Path(realpath(self.get_config(TUSHARE_META_DIR_KEY) or self._get_default_data_dir('meta')))
        if not meta_dir.exists():
            meta_dir.mkdir(parents=True)
            # os.makedirs(meta_dir)
        self.set_tutake_meta_dir(meta_dir)

        self.logger_config_file = self._get_logger_config()
        if self.logger_config_file:
            setup_logging(self.logger_config_file)

        logging.getLogger("tutake.config").debug("Set default config. {}".format(self))

    def __str__(self):
        return f"ConfigFile: {self.config_file}" \
               f"\n\t{TUTAKE_DRIVER_URL_KEY}:\t{self.get_config(TUTAKE_DRIVER_URL_KEY)}" \
               f"\n\t{TUSHARE_TOKEN_KEY}:\t{self.get_tushare_token()}" \
               f"\n\t{TUTAKE_PROCESS_THREAD_CNT_KEY}:\t{self.get_process_thread_cnt()}" \
               f"\n\t{TUTAKE_LOGGING_CONFIG_KEY}:\t{self.logger_config_file}" \
               f"\n\t{TUTAKE_SCHEDULER_CONFIG_KEY}:\t{self.get_config(TUTAKE_SCHEDULER_CONFIG_KEY)}"

    def check(self):
        if self.empty:
            raise Exception(f"Tutake config is empty, not support invoke process api.")


    def _load_config_file(self, config_file: str) -> DotConfig:
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf8') as stream:
                return DotConfig(yaml.safe_load(stream))
        else:
            print("Config file is not exits, use default empty config instead. Pls set config in %s" % config_file)
        return DotConfig()

    def merge_config(self, **_config):
        if _config is not None:
            for key in _config:
                new_key = key.replace("_", ".")
                self.set_config(new_key, _config[key])

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

    def is_test_mode(self):
        return self.get_config(TUTAKE_TEST_MODE, False)

    def set_tutake_data_dir(self, _dir: Path = None):
        if _dir:
            self.set_config(TUTAKE_DRIVER_URL_KEY, self._get_default_driver_url(_dir))

    def set_tutake_meta_dir(self, _dir=None):
        if _dir:
            self.set_config(TUSHARE_META_DRIVER_URL_KEY, self._get_default_driver_url(_dir))

    def _get_default_data_dir(self, dir_name):
        # db_name = 'tushare_stock_basic.db'
        if dir_name == 'meta':
            db_name = 'tushare_meta.db'
        _dir = Path(dirname(self.config_file), dir_name)
        # "%s/%s" % (dirname(self.config_file), dir_name)
        # _dir = Path(dirname(self.config_file), dir_name)
        if _dir.exists():
            # os.path.exists("%s/%s" % (_dir, db_name)):
            return _dir
        else:
            return Path.home().joinpath(".tutake")
            # return "%s/%s" % (Path.home(), '.tutake')

    def get_tutake_data_dir(self):
        return Path(realpath(self.get_config(TUTAKE_DATA_DIR_KEY) or self._get_default_data_dir('database')))

    def _get_default_driver_url(self, path: Path, sub_dir=None):
        if path is None:
            path = Path.home().joinpath(".tutake")
        if sub_dir:
            path = path.joinpath(sub_dir)
            # "%s/%s" % (path, sub_dir)
        if not path.exists():
            path.mkdir(parents=True)
            # os.makedirs(path)
        path = os.path.expanduser(path)
        return f'{TUTAKE_DATABASE_TYPE}:///{path}'

    @staticmethod
    def __set(config: DotConfig, k, v):
        return config.set(k, v)

    def get_remote_address(self):
        return self.get_config(TUTAKE_REMOTE_SERVER_KEY, None)
        # if address is not None:
        #     url_parts = urlparse(address)
        #     hostname = url_parts.hostname
        #     port = url_parts.port
        #     return (hostname, port)
        # return None

    def get_process_forbidden(self):
        return self.get_config(TUTAKE_PROCESS_FORBIDDEN_CONFIG_KEY)

    def get_sqlite_timeout(self):
        return self.get_config(TUTAKE_SQLITE_TIMEOUT_CONFIG_KEY, 5)

    def get_data_driver_url(self, data_file="tutake.duckdb"):
        url = self.require_config(TUTAKE_DRIVER_URL_KEY)
        suffix = ""
        if self.is_test_mode():
            suffix = ".test"
        if not data_file:
            return f"{url}{suffix}"
        else:
            return f"{url}{os.sep}{data_file}{suffix}"
        # if os.name == 'nt':
        #     return f"{url}{os.sep}{data_file}".replace("\\", "\\\\")
        # else:
        #     return f"{url}{os.sep}{data_file}"

    def get_meta_sqlite_driver_url(self):
        return self.require_config(TUSHARE_META_DRIVER_URL_KEY)

    def set_tushare_token(self, tushare_token):
        if tushare_token:
            self.set_config(TUSHARE_TOKEN_KEY, tushare_token)

    def get_tushare_token(self):
        self.check()
        token = self.get_config(TUSHARE_TOKEN_KEY)
        if token is None:
            tokens = self.get_config(TUSHARE_TOKENS_KEY)
            if tokens:
                return tokens[next(iter(tokens))][0]
        return token

    def _get_logger_config(self):
        logger_config_path = self.get_config(TUTAKE_LOGGING_CONFIG_KEY)
        if logger_config_path and not os.path.isabs(logger_config_path):
            # 如果日志配置文件是相对路径，转换成绝对路径
            logger_config_path = join(abspath(dirname(self.config_file)), logger_config_path)
        if not logger_config_path or not os.path.exists(logger_config_path):
            # logging.warning(
            #     f"Logger config file is not config or not exists. {logger_config_path}")
            logger_config_path = f"{file_dir(__file__)}/ts_logger.yml"
            # logging.warning(f"Use default logger config: {logger_config_path}")
        return logger_config_path

    def get_process_thread_cnt(self):
        return self.get_config(TUTAKE_PROCESS_THREAD_CNT_KEY, 4)
