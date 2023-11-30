"""
Tushare sf_month接口
获取月度社会融资数据
数据接口-宏观经济-国内宏观-金融-货币供应量-社融数据（月）  https://tushare.pro/document/2?doc_id=310
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
    return "2000"


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
