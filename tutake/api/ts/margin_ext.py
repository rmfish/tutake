"""
Tushare margin接口
获取融资融券每日交易汇总数据,数据开始于2010年，每日9点更新
数据接口-沪深股票-市场参考数据-融资融券交易汇总  https://tushare.pro/document/2?doc_id=58
"""
from tutake.api.ts.date_utils import start_end_step_params


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
    return start_end_step_params(self, "20100331", 180)
