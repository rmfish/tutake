"""
资产负债表
接口：balancesheet，可以通过数据工具调试和查看数据。
描述：获取上市公司资产负债表
"""

from tutake.api.ts.date_utils import quarter_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return "end_date desc,f_ann_date"


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "7000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, date_col='ann_date')
