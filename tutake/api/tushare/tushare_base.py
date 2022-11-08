import tushare as ts

from tutake.utils.config import tutake_config


class TuShareBase(object):
    def __init__(self):
        tushare_token = tutake_config.get_tushare_token()
        if tushare_token:
            self.t_api = ts.pro_api(tushare_token)
        tushare_tokens = tutake_config.get_config('tushare.tokens')
        if tushare_tokens and len(tushare_tokens) > 1:
            self.t_apis = {i: ts.pro_api(tushare_tokens[i]) for i in range(len(tushare_tokens))}
            self.token_index = 0
        assert self.tushare_api is not None or self.t_apis is not None, 'Tushare token is required, pls config it in config.yaml'

    def tushare_api(self):
        if self.t_apis:
            api = self.t_apis[self.token_index]
            self.token_index = (self.token_index + 1) % len(self.t_apis.keys())
            return api
        else:
            return self.t_api
