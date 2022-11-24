from functools import partial

import tushare

from tutake.api.ts.dao import DAO
from tutake.utils.config import TutakeConfig


class TushareQuery:
    def __init__(self, config):
        token = config.get_tushare_token()
        if token != '':
            self.tushare = tushare.pro_api(token)
        self.config = config
        self.dao = DAO(config, True)

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


def pro_api(token='', data_dir: str = None) -> TushareQuery:
    config = TutakeConfig()
    config.set_tushare_token(token)
    config.set_tutake_data_dir(data_dir)
    return TushareQuery(config)


def pro_bar(api: TushareQuery, ts_code='', start_date='', end_date='', freq='D', asset='E', exchange='', adj=None,
            ma=[], factors=None, adjfactor=False, offset=None, limit=None, contract_type=''):
    return tushare.pro_bar(ts_code, api, start_date, end_date, freq, asset, exchange, adj, ma, factors, adjfactor,
                           offset,
                           limit, contract_type)


if __name__ == "__main__":
    api = pro_api("aec595052cb10051350a6a164f41b344b922f0b3ee206efdec2e0082")
    print(api.stock_basic(fields='name,ts_code'))
    df = pro_bar(api, ts_code='000001.SZ', adj='hfq', start_date='20180101', end_date='20181011')
    print(df)
