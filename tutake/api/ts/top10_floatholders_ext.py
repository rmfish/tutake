"""
Tushare top10_floatholders接口
获取上市公司前十大流通股东数据。
数据接口-沪深股票-市场参考数据-前十大流通股东  https://tushare.pro/document/2?doc_id=62
"""
from tutake.api.ts.date_utils import get_latest_quarter, quarter_params, day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "5000"


def prepare_ext(self):
    """
    同步历史数据准备工作
    """
    # self.delete_by(end_date=get_latest_quarter(self))


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    # return quarter_params(self, '20001231', 'end_date', 'period')
    return day_by_day_params(self, '20050129', 'ann_date')
