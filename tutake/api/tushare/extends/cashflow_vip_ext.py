"""
现金流量表
接口：cashflow，可以通过数据工具调试和查看数据。
描述：获取上市公司现金流量表
"""

from tutake.api.process_report import ProcessType
from tutake.api.tushare.extends.date_utils import financial_report_time_params


def default_cron_express_ext(self) -> str:
    return "0 1 * * *"


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return "end_date desc,f_ann_date"


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "6400"


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return financial_report_time_params(self, process_type)


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
