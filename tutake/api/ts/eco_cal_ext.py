"""
Tushare eco_cal接口
获取全球财经日历、包括经济事件数据更新
数据接口-债券-全球财经事件  https://tushare.pro/document/2?doc_id=233
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
    return "100"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '19700101', 10, 'date')
