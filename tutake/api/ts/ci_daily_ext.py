"""
Tushare ci_daily接口
获取国际主要指数日线行情
数据接口-指数-中信行业指数日行情  https://tushare.pro/document/2?doc_id=308
"""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "4000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return []
