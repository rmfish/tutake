import pendulum

from tutake.api.checker import DataChecker
from tutake.api.ts.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date,ts_code"


def default_limit_ext(self):
    return '6000'


def prepare_ext(self):
    """
    同步历史数据准备工作
    :return:
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '19901215', step=3)
    # return daily_params(self, lambda x: self.api.stock_basic.count(),
    #                     lambda x: self.api.stock_basic.column_data(['ts_code', 'list_date']))


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params


def check_ext(self, checker: DataChecker, **kwargs):
    start_date = pendulum.parse(kwargs['start_date'])
    end_date = pendulum.parse(kwargs['end_date'])
    time = None
    while start_date <= end_date:
        check_time = start_date.format("YYYYMM")
        if check_time != time:
            print(f"Start check time of {check_time}")
            time = check_time
        trade_date = start_date.format("YYYYMMDD")
        tushare = self.fetch_and_append(trade_date=trade_date)
        db = self.daily(fields='ts_code', trade_date=trade_date)
        if tushare.size() != db.shape[0]:
            print(trade_date, tushare.size(), db.shape[0])
        start_date = start_date.add(days=1)
