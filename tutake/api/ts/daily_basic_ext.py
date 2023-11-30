"""
Tushare daily_basic接口
交易日每日15点～17点之间,获取全部股票每日重要的基本面指标，可用于选股分析、报表展示等。
数据接口-沪深股票-行情数据-每日指标  https://tushare.pro/document/2?doc_id=32
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
    return "5200"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '19901215', step=2)
