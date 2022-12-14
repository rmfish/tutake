"""
利润表
接口：income，可以通过数据工具调试和查看数据。
描述：获取上市公司财务利润表数据
积分：用户需要至少2000积分才可以调取，具体请参阅积分获取办法

提示：当前接口只能按单只股票获取其历史数据，如果需要获取某一季度全部上市公司数据，请使用income_vip接口（参数一致），需积攒5000积分。
"""

from tutake.api.ts.date_utils import quarter_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "end_date desc,f_ann_date"


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '9000'


def prepare_ext(self):
    """
    同步历史数据准备工作
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, '19901231', date_col='ann_date')


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
