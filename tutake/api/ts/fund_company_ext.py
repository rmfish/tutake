"""
Tushare fund_company接口
获取公募基金管理人列表
数据接口-公募基金-基金管理人  https://tushare.pro/document/2?doc_id=118
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
    return ""


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return []
