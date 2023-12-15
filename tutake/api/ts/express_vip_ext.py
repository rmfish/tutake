"""
获取上市公司业绩快报
"""
from tutake.api.ts.date_utils import quarter_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'end_date desc,ann_date desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '5000'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, '20041231', date_col='ann_date')
