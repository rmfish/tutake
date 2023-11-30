"""
业绩预告
接口：forecast，可以通过数据工具调试和查看数据。
描述：获取业绩预告数据
权限：用户需要至少800积分才可以调取，具体请参阅积分获取办法
"""

from tutake.api.ts.date_utils import quarter_params


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


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, date_col='ann_date')
