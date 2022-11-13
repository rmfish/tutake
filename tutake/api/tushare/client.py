import logging
from functools import partial

import tushare as ts

from tutake.api.tushare.dao import DAO
from tutake.api.tushare.process import ProcessType
from tutake.utils.config import tutake_config


def pro_api(token='', data_dir: str = None):
    return TushareQuery(token, data_dir)


def process_api(config: dict = None):
    return TushareProcess(config)


class TushareProcess:
    def __init__(self, _config: dict = None):
        tutake_config.merge_config(_config)
        self.dao = DAO()

    def process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        api = self.dao.__getattr__(api_name)
        if api is not None:
            return api.process(process_type)
        else:
            return None

    def __getattr__(self, name):
        return partial(self.process, name)


class TushareQuery:
    def __init__(self, tushare_token, data_dir: str = None):
        if tushare_token != '':
            self.tushare = ts.pro_api(tushare_token)
        if data_dir is not None:
            tutake_config.set_tutake_data_dir(data_dir)
        self.dao = DAO()

    def query(self, api_name, fields='', **kwargs):
        api = self.dao.__getattr__(api_name)
        if api is None:
            return self.fail_over(api_name, fields, **kwargs)
        method = getattr(api, api_name)
        if method is not None:
            return method(fields, **kwargs)
        return None

    def fail_over(self, api_name, fields='', **kwargs):
        if self.tushare is not None:
            return self.tushare.query(api_name, fields, **kwargs)

    def __getattr__(self, name):
        return partial(self.query, name)


if __name__ == "__main__":
    dao = pro_api("aec595052cb10051350a6a164f41b344b922f0b3ee206efdec2e0082")
    # print(dao.stock_basic(fields='name,ts_code,', name='ST国华'))
    print(dao.shibor(start_date='20180101', end_date='20181101'))
