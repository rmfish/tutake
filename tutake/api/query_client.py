from functools import partial

import tushare
from pandas import DataFrame

from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.xq.xueqiu_api import XueQiuAPI


class TushareQuery:
    def __init__(self, config):
        token = config.get_tushare_token()
        if token and token != '':
            self.tushare = tushare.pro_api(token)
        self.config = config
        self.api = TushareAPI(config)

    def query(self, api_name, fields='', **kwargs) -> DataFrame:
        _api = self.api.__getattr__(api_name)
        if _api is None:
            return self.fail_over(api_name, fields, **kwargs)
        method = getattr(_api, api_name)
        if method is not None:
            return method(fields, **kwargs)
        return None

    def fail_over(self, api_name, fields='', **kwargs):
        if self.tushare is not None:
            return self.tushare.query(api_name, fields, **kwargs)

    def apis(self):
        """
        获取支持的所有api
        :return:
        """
        return self.api.all_apis()

    def pro_bar(self, ts_code='', start_date='', end_date='', freq='D', asset='E', exchange='', adj=None,
                ma=[], factors=None, adjfactor=False, offset=None, limit=None, contract_type=''):
        return tushare.pro_bar(ts_code, self, start_date, end_date, freq, asset, exchange, adj, ma, factors, adjfactor,
                               offset,
                               limit, contract_type)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            return self.api.__getattr__(name[1:])
        return partial(self.query, name)


class XueQiuQuery:
    def __init__(self, config):
        self.config = config
        self.api = XueQiuAPI(config)

    def query(self, api_name, fields='', **kwargs):
        api = self.api.__getattr__(api_name)
        method = getattr(api, api_name)
        if method is not None:
            return method(fields, **kwargs)
        return None

    def __getattr__(self, name: str):
        if name.startswith("_"):
            return self.api.__getattr__(name[1:])
        return partial(self.query, name)

    def apis(self):
        """
        获取支持的所有api
        :return:
        """
        return self.api.all_apis()
