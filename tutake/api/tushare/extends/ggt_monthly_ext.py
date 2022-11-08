import pendulum

from tutake.api.tushare.process import ProcessType


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
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
    str_format = "YYYYMM"
    start_record_month = pendulum.from_format('201411', str_format).last_of('month')  # 最早的数据记录
    month_period = 1000
    if ProcessType.HISTORY == process_type:
        min_month = self.min("month", condition="month is not null")
        if min_month is not None:
            end_month = pendulum.parse(min_month).add(months=-1).last_of('month')
        else:
            end_month = pendulum.now().last_of('month')
        while end_month.diff(start_record_month, abs=False).in_days() < 27:
            start_month = end_month.add(months=-month_period)
            params.append({"start_date": start_month.format(str_format), "end_date": end_month.format(str_format)})
            end_month = start_month.add(months=-month_period)
    else:
        max_month = self.max("month")
        if max_month is not None:
            start_month = pendulum.parse(max_month).add(months=1)
        else:
            start_month = start_record_month
        while start_month.diff(pendulum.now(), False).in_days() > 27:
            end_month = start_month.add(months=month_period)
            params.append({"start_date": start_month.format(str_format), "end_date": end_month.format(str_format)})
            start_month = start_month.add(months=month_period)
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
