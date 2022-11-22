"""
获取备用行情，包括特定的行情指标。量比、换手率、成交量、流通市值、强弱度(%)...
"""
from tutake.api.process_report import ProcessType
from tutake.api.tushare.date_utils import start_end_step_params


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date desc,ts_code"


def default_limit_ext(self):
    return '5000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    :return:
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, process_type, step=3, start_date='20170614')
    # import pendulum
    # start = pendulum.parse('20170614')
    # now = pendulum.now()
    # params = []
    # while start < now:
    #     params.append({"trade_date": now.format('YYYYMMDD')})
    #     now = now.add(days=-1)
    # return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    # min_date = self.min("trade_date", "trade_date = '%s'" % params['trade_date'])
    # if min_date == params['trade_date']:
    #     return None
    return params
