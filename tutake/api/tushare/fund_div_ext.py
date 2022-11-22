"""
Tushare fund_div接口
获取公募基金分红数据
数据接口-公募基金-基金分红  https://tushare.pro/document/2?doc_id=120
"""

from tutake.api.process_report import ProcessType
from tutake.api.tushare.date_utils import day_by_day_params


def default_cron_express_ext(self) -> str:
    return "10 0 * * *"


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'ann_date desc,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "1200"


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return day_by_day_params(self, process_type, "19990329", "ann_date")


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
