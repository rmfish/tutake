"""
分红送股数据
"""
from tutake.api.process_report import ProcessType


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'end_date desc,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '10000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return self.dao.stock_basic.column_data(['ts_code'])


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
