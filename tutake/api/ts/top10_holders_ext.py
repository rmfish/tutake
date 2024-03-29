"""
Tushare top10_holders接口
获取上市公司前十大股东数据，包括持有数量和比例等信息。
数据接口-沪深股票-市场参考数据-前十大股东  https://tushare.pro/document/2?doc_id=61
"""
from tutake.api.ts.date_utils import day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "5000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, '20050129', 'ann_date')
