"""
Tushare us_tycr接口
美国国债每日收益率曲线
数据接口-宏观经济-国际宏观-美国利率-国债收益率曲线利率  https://tushare.pro/document/2?doc_id=219
"""
from tutake.api.ts.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return ""


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


def prepare_ext(self):
    """
    同步历史数据准备工作
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, start_date='19900102', step=2000, date_col='date')


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params