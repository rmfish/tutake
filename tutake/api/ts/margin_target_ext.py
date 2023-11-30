"""
Tushare margin_target接口
获取全市场融资融券标的
数据接口-沪深股票-市场参考数据-融资融券标的  https://tushare.pro/document/2?doc_id=286
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
    return "4500"


def prepare_ext(self):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
