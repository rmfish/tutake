"""
Tushare report_rc接口
获取券商（卖方）每天研报的盈利预测数据，数据从2010年开始，每晚19~22点更新当日数据
数据接口-沪深股票-特色数据-券商盈利预测数据  https://tushare.pro/document/2?doc_id=292
"""


def default_cron_express_ext(self) -> str:
    return ""


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


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return []


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
