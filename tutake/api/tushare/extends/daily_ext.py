from tutake.api.process_report import ProcessType
from tutake.api.tushare.extends.date_utils import daily_params, daily_params_loop


def default_cron_express_ext(self) -> str:
    return "10 17 * * *"


def default_order_by_ext(self) -> str:
    return "trade_date desc,ts_code"


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
    return daily_params(self, process_type, lambda x: self.dao.stock_basic.column_data(['ts_code', 'list_date']))


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return daily_params_loop(self, process_type)
