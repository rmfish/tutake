from tutake.api.process_report import ProcessType
from tutake.api.ts.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date desc,ts_code"


def default_limit_ext(self):
    return '5000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, process_type, start_date='20070101', step=3)


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
