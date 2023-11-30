"""
Tushare stock_mx接口
获取小佩数据动量因子数据，可以获取股票动能评级数据，包括最新及过去历史数据
数据接口  https://tushare.pro/document/2?doc_id=300
"""
from tutake.api.ts.date_utils import day_by_day_params


def default_cron_express_ext(self):
    return None

def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "6000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, "20140101", "trade_date")
