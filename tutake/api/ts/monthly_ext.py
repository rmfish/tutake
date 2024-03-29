from tutake.api.checker import check_by_date
from tutake.api.ts.date_utils import m_by_m_params


def default_cron_express_ext(self) -> str:
    return "10 0 1 * *"


def default_order_by_ext(self) -> str:
    return "trade_date,ts_code"


def default_limit_ext(self):
    return '4500'

    self.delete_by(trade_date='20230831')


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return m_by_m_params(self, '19901231')


def check_ext(self, **kwargs):
    check_by_date(self, self.monthly, force_start=kwargs.get("force_start"), default_start='19901231',
                  date_apply=lambda date: date.add(months=1).last_of("month"), print_step=10)
