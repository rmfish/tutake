"""
Tushare cn_gdp接口
获取国民经济之GDP数据
数据接口-宏观经济-国内宏观-国民经济-国内生产总值（GDP）  https://tushare.pro/document/2?doc_id=227
"""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'quarter desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "10000"


def prepare_write_ext(self, writer, **kwargs):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def need_to_process_ext(self, **kwargs):
    from tutake.api.ts.date_utils import min_count_and_last_process
    return min_count_and_last_process(self, last_process_day=30)


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
