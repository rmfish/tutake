from tutake.api.tushare.process import ProcessType


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
    import pendulum
    start = pendulum.parse('20170614')
    now = pendulum.now()
    params = []
    while start < now:
        params.append({"trade_date": now.format('YYYYMMDD')})
        now = now.add(days=-1)
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    min_date = self.min("trade_date", "trade_date = '%s'" % params['trade_date'])
    if min_date == params['trade_date']:
        return None
    return params
