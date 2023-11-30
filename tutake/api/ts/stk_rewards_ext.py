import numpy as np

from tutake.api.ts.date_utils import day_by_day_params
from tutake.utils import utils


def default_order_by_ext(self) -> str:
    return "ann_date desc,ts_code"


def default_limit_ext(self):
    return '4000'

    cnt = self.count()
    if cnt < 100000:
        self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    cnt = self.count()
    if cnt < 1000000:
        return self.api.stock_basic.column_data(['ts_code'])
    else:
        stocks = [s['ts_code'] for s in self.api.stock_basic.column_data(['ts_code'])]
        stocks = utils.chunks(stocks, 500)
        dates = day_by_day_params(self, "19911231", date_column="end_date")
        params = []
        for date in dates:
            for stock in stocks:
                params.append({"end_date": date['end_date'], "ts_code": ','.join(stock)})
        return params
