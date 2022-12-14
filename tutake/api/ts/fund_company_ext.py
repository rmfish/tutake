"""
Tushare fund_company接口
获取公募基金管理人列表
数据接口-公募基金-基金管理人  https://tushare.pro/document/2?doc_id=118
"""

from tutake.api.process_report import ProcessType


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return ""


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def query_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return []


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
