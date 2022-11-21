"""
接口：moneyflow_hsgt，可以通过数据工具调试和查看数据。
描述：获取沪股通、深股通、港股通每日资金流向数据，每次最多返回300条记录，总量不限制。每天18~20点之间完成当日更新
积分要求：2000积分起，5000积分每分钟可提取500次
"""

from tutake.api.process_report import ProcessType
from tutake.api.tushare.extends.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return "0 1 * * *"


def default_order_by_ext(self) -> str:
    return "trade_date desc"


def default_limit_ext(self):
    return '300'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, process_type, '20141117', 300)


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
