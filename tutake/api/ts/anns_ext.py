"""
Tushare anns接口
获取上市公司公告数据及原文文本，数据从2000年开始。
数据接口-另类数据-上市公司公告原文  https://tushare.pro/document/2?doc_id=176
"""

from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '150'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, start_date="20000516", step=1, date_col='ann_date')
