"""
接口：moneyflow_hsgt，可以通过数据工具调试和查看数据。
描述：获取沪股通、深股通、港股通每日资金流向数据，每次最多返回300条记录，总量不限制。每天18~20点之间完成当日更新
积分要求：2000积分起，5000积分每分钟可提取500次
"""

from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    return "trade_date desc"


def default_limit_ext(self):
    return '300'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '20141117', 300)
