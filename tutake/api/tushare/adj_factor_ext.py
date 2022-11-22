"""
获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子。更新时间：早上9点30分
"""
from tutake.api.process_report import ProcessType
from tutake.api.tushare.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date desc"


def default_limit_ext(self):
    return '6000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    :return:
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, process_type, "19901211")


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params

