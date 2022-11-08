from tutake.api.tushare.process import ProcessType
import pendulum

"""
接口：moneyflow_hsgt，可以通过数据工具调试和查看数据。
描述：获取沪股通、深股通、港股通每日资金流向数据，每次最多返回300条记录，总量不限制。每天18~20点之间完成当日更新
积分要求：2000积分起，5000积分每分钟可提取500次
"""


def default_order_by_ext(self) -> str:
    return "trade_date desc"


def default_limit_ext(self):
    return '300'


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
    day_period = 300
    if ProcessType.HISTORY == process_type:
        min_date = self.min("trade_date", condition="trade_date is not null")
        if min_date is not None:
            end_date = pendulum.parse(min_date).add(days=-1)
        else:
            end_date = pendulum.now()
        while end_date > start_record_date:
            start_date = end_date.add(days=-day_period)
            params.append({"start_date": start_date.format(str_format), "end_date": end_date.format(str_format)})
            end_date = start_date.add(days=-day_period)
    else:
        max_date = self.max("trade_date")
        if max_date is not None:
            start_date = pendulum.parse(max_date)
        else:
            start_date = start_record_date.add(days=-1)
        while start_date.diff(pendulum.now(), False).in_hours() > 0:
            end_date = start_date.add(days=day_period)
            params.append({"start_date": start_date.format(str_format), "end_date": end_date.format(str_format)})
            start_date = start_date.add(days=day_period)
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
