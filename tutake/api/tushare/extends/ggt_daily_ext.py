"""
港股通每日成交统计
接口：ggt_daily
描述：获取港股通每日成交信息，数据从2014年开始
限量：单次最大1000，总量数据不限制
积分：用户积2000积分可调取，5000积分以上频次相对较高，请自行提高积分，具体请参阅积分获取办法

"""
import pendulum

from tutake.api.tushare.process import ProcessType

def default_limit_ext(self):
    return '1000'

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
    day_period = 1000
    if ProcessType.HISTORY == process_type:
        min_date = self.min("trade_date", condition="trade_date is not null")
        if min_date is not None:
            start_date = pendulum.parse(min_date)
        else:
            start_date = pendulum.now()
        while start_date > start_record_date:
            end_date = start_date.add(days=-day_period)
            start_date = end_date.add(days=-day_period)
            params.append({"start_date": start_date.format(str_format), "end_date": end_date.format(str_format)})
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
