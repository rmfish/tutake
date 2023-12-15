"""
Tushare balancesheet接口
获取上市公司资产负债表
数据接口-沪深股票-财务数据-资产负债表  https://tushare.pro/document/2?doc_id=36
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
