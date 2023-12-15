"""
Tushare top_inst接口
龙虎榜机构交易明细数据,数据开始于2005年，每日晚8点更新
数据接口-沪深股票-市场参考数据-龙虎榜机构交易明细  https://tushare.pro/document/2?doc_id=107
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
    return "10000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, '20050105', 'trade_date')
