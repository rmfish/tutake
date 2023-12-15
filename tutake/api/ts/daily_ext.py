import pendulum

from tutake.api.checker import check_by_date
from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    return "trade_date desc,ts_code desc"


def default_limit_ext(self):
    return '6000'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '19901215', step=3)
    # return daily_params(self, lambda x: self.api.stock_basic.count(),
    #                     lambda x: self.api.stock_basic.column_data(['ts_code', 'list_date']))


def check_ext(self, **kwargs):
    check_by_date(self, self.daily, force_start=kwargs.get("force_start"), default_start='19901215',
                  date_apply=lambda date: date.add(days=1))
