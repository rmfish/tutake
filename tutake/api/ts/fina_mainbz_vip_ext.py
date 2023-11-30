"""
Tushare fina_mainbz_vip接口
获得上市公司主营业务构成，分地区和产品两种方式
数据接口-沪深股票-财务数据-主营业务构成  https://tushare.pro/document/2?doc_id=81
"""
from tutake.api.ts.date_utils import get_latest_quarter, quarter_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "10000"


def prepare_ext(self):
    """
    同步历史数据准备工作
    """
    period = get_latest_quarter(self)
    self.delete_by(end_date=period)


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return quarter_params(self, '20001231', 'end_date', 'period')
