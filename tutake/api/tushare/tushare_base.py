import tushare as ts

from tutake.utils.config import tutake_config


class TuShareBase(object):
    def __init__(self):
        self.tushare_token = tutake_config.get_tushare_token()
        assert self.tushare_token is not None and self.tushare_token != '', 'Tushare token is required, pls config it in config.yaml'

    def tushare_api(self):
        return ts.pro_api(self.tushare_token)
