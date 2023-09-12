"""
Tushare index_monthly接口
获取指数月线行情,每月更新一次
数据接口-指数-指数月线行情  https://tushare.pro/document/2?doc_id=172
"""
from tutake.api.checker import check_by_date
from tutake.api.ts.date_utils import m_by_m_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'ts_code,trade_date'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "1000"


def prepare_ext(self):
    """
    同步历史数据准备工作
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return m_by_m_params(self, '19900101', date_column='trade_date')


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params


def check_ext(self, **kwargs):
    check_by_date(self, self.index_monthly, force_start=kwargs.get("force_start"), default_start='19900101',
                  date_apply=lambda date: date.add(months=1).last_of("month"), print_step=10, diff_repair=None)
