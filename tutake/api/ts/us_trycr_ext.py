"""
Tushare us_trycr接口
获取美国国债实际收益率曲线利率数据
数据接口-宏观经济-国际宏观-美国利率-国债实际收益率曲线利率  https://tushare.pro/document/2?doc_id=220
"""
from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'date desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "2000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, start_date='20030101', step=1500, date_col='date')
