"""
获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子。更新时间：早上9点30分
"""
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
    return start_end_step_params(self, "19901211")


def check_ext(self, **kwargs):
    check_by_date(self, self.adj_factor, force_start=kwargs.get("force_start"), default_start='19901219',
                  date_apply=lambda date: date.add(days=1))
