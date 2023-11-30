"""
Tushare limit_list_d接口
获取沪深A股每日涨跌停、炸板数据情况，数据从2020年开始
数据接口-沪深股票-特色数据-涨跌停和炸板数据  https://tushare.pro/document/2?doc_id=298
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
    return "500"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '20191128')
