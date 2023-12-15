"""
Tushare hk_hold接口
获取沪深港股通持股明细，数据来源港交所。下个交易日8点更新
数据接口-沪深股票-特色数据-沪深股通持股明细  https://tushare.pro/document/2?doc_id=188
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
    return "4200"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '20160629')
