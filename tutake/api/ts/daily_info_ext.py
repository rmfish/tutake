"""
Tushare daily_info接口
获取交易所股票交易统计，包括各板块明细
数据接口-指数-沪深市场每日交易统计  https://tushare.pro/document/2?doc_id=215
"""
from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date,ts_code'


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
    return start_end_step_params(self, '19901218', step=30)
