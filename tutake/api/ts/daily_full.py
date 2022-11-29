import pandas as pd

from tutake.api.ts.tushare_api import TushareAPI


class DailyFull(object):
    def __init__(self, config):
        self.api = TushareAPI(config)

    def daily_full(self, fields='', **kwargs):
        if not kwargs["ts_code"]:
            raise Exception("ts_code is required!")
        daily = self.api.daily.daily(**kwargs)
        if daily.shape[0] > 0:
            kwargs["end_date"] = daily['trade_date'].max()
            kwargs["start_date"] = daily['trade_date'].min()
            kwargs["limit"] = daily.shape[0] * 2
            kwargs["offset"] = 0
            daily_basic = self.api.daily_basic.daily_basic(**kwargs)
            daily_full = pd.merge(daily, daily_basic, how='left', on=['ts_code', 'trade_date'])
            daily_full.drop('close_y', axis=1, inplace=True)
            daily_full.rename(columns={"close_x": "close"}, inplace=True)
            return daily_full
        return daily
