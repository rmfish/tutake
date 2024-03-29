"""
分红送股数据
"""
from tutake.api.ts.date_utils import day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'end_date desc,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '10000'


def prepare_write_ext(self, writer, **kwargs):
    """
    同步历史数据准备工作
    """
    # self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, "19910316")
