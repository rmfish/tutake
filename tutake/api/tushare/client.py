from functools import partial

from tutake.api.tushare.dao import DAO
import tushare as ts


def pro_api(token=''):
    return TushareDAO(token)


class TushareDAO:
    def __init__(self, tushare_token):
        self.dao = DAO()
        if tushare_token != '':
            self.tushare = ts.pro_api(tushare_token)

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
