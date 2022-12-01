import os
from functools import partial

import tushare

from tutake.api.ts.tushare_api import TushareAPI
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import file_dir


class TushareQuery:
    def __init__(self, config):
        token = config.get_tushare_token()
        if token and token != '':
            self.tushare = tushare.pro_api(token)
        self.config = config
        self.api = TushareAPI(config)

    def query(self, api_name, fields='', **kwargs):
        api = self.api.__getattr__(api_name)
        if api is None:
            return self.fail_over(api_name, fields, **kwargs)
        method = getattr(api, api_name)
        if method is not None:
            return method(fields, **kwargs)
        return None

    def fail_over(self, api_name, fields='', **kwargs):
        if self.tushare is not None:
            return self.tushare.query(api_name, fields, **kwargs)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            return self.api.__getattr__(name[1:])
        return partial(self.query, name)


def pro_api(config_file_path) -> TushareQuery:
    config = __config_from_file(config_file_path)
    if not config:
        raise Exception(f"Config file {config_file_path} is not exists, pls check it.")
    return TushareQuery(config)


def __config_from_file(config_file_path):
    if not os.path.exists(config_file_path):
        return None
    return TutakeConfig(file_dir(config_file_path), os.path.basename(config_file_path))


def pro_bar(api: TushareQuery, ts_code='', start_date='', end_date='', freq='D', asset='E', exchange='', adj=None,
            ma=[], factors=None, adjfactor=False, offset=None, limit=None, contract_type=''):
    return tushare.pro_bar(ts_code, api, start_date, end_date, freq, asset, exchange, adj, ma, factors, adjfactor,
                           offset,
                           limit, contract_type)
