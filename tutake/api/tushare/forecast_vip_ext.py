"""
业绩预告
接口：forecast，可以通过数据工具调试和查看数据。
描述：获取业绩预告数据
权限：用户需要至少800积分才可以调取，具体请参阅积分获取办法
"""

from tutake.api.process_report import ProcessType
from tutake.api.tushare.date_utils import quarter_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return "end_date desc,ts_code"


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '3500'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, process_type, date_col='ann_date')


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params