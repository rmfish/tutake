"""
Tushare fund_sales_vol接口
获取销售机构公募基金销售保有规模数据，本数据从2021年Q1开始公布，季度更新
数据接口-财富管理-基金销售行业数据-销售机构公募基金销售保有规模  https://tushare.pro/document/2?doc_id=266
"""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'year desc,quarter desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "500"


def prepare_write_ext(self, writer, **kwargs):
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


def need_to_process_ext(self, **kwargs):
    from tutake.api.ts.date_utils import min_count_and_last_process
    return min_count_and_last_process(self, last_process_day=30)
