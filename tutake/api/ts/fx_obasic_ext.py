"""
Tushare fx_obasic接口
获取海外外汇基础信息，目前只有FXCM交易商的数据
数据接口-外汇-外汇基础信息（海外）  https://tushare.pro/document/2?doc_id=178
"""


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


def prepare_ext(self):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
