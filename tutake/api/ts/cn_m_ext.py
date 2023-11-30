"""
Tushare cn_m接口
获取货币供应量月度数据
数据接口-宏观经济-国内宏观-金融-货币供应量-货币供应量（月）  https://tushare.pro/document/2?doc_id=242
"""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'month desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "5000"


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
