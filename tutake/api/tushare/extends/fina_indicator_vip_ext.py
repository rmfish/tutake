import pendulum

from tutake.api.tushare.process import ProcessType


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'end_date desc,ann_date'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '12000'


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
    start_record_period = pendulum.parse('20041231').last_of("quarter")  # 最早的数据记录
    if ProcessType.HISTORY == process_type:
        min_period = self.min("end_date", condition="end_date is not null")
        if min_period is not None:
            period = pendulum.parse(min_period).add(months=-3).last_of('quarter')
        else:
            period = pendulum.now().last_of("quarter")
        while period >= start_record_period:
            params.append({"period": period.format(str_format)})
            period = period.add(months=-3).last_of("quarter")
    else:
        max_period = self.max("end_date")
        if max_period is not None:
            period = pendulum.parse(max_period).add(months=3).last_of("quarter")
        else:
            period = start_record_period
        while period.diff(pendulum.now().last_of('quarter'), False).in_days() > 0:
            params.append({"period": period.format(str_format)})
            period = period.add(months=3).last_of("quarter")
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params