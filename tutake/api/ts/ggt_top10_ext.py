import pendulum

from tutake.api.process_report import ProcessType


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date,ts_code"


def default_limit_ext(self):
    return ''


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    params = []
    str_format = "YYYYMMDD"
    start_record_date = pendulum.parse('20141117')  # 最早的数据记录
    if ProcessType.HISTORY == process_type:
        min_date = self.min("trade_date", condition="trade_date is not null")
        if min_date is not None:
            trade_date = pendulum.parse(min_date)
        else:
            trade_date = pendulum.now()
        while trade_date > start_record_date:
            params.append({"trade_date": trade_date.format(str_format)})
            trade_date = trade_date.add(days=-1)
    else:
        max_date = self.max("trade_date")
        if max_date is not None:
            trade_date = pendulum.parse(max_date).add(days=1)
        else:
            trade_date = start_record_date
        while trade_date.diff(pendulum.now(), False).in_hours() > 0:
            params.append({"trade_date": trade_date.format(str_format)})
            trade_date = trade_date.add(days=1)
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
