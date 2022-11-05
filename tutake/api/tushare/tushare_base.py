from tutake.utils.config import config
import tushare as ts


class TuShareBase(object):
    def __init__(self):
        self.tushare_token = config.get('tushare').get('token')
        assert self.tushare_token is not None and self.tushare_token != '', 'Tushare token is required, pls config it in config.yaml'

    def tushare_api(self):
        return ts.pro_api(self.tushare_token)
