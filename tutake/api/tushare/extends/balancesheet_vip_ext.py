"""
资产负债表
接口：balancesheet，可以通过数据工具调试和查看数据。
描述：获取上市公司资产负债表
"""
import pendulum

from tutake.api.tushare.process import ProcessType


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return "end_date desc,f_ann_date"


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "100000000"


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
    start_record_period = pendulum.parse('19901231')  # 最早的数据记录
    max_period = self.max("end_date")
    if max_period is None or pendulum.now().diff(
            pendulum.parse(max_period), abs=False).in_months() > 3 or ProcessType.HISTORY == process_type:
        min_period = self.min("end_date", condition="end_date is not null")
        if min_period is not None:
            period = pendulum.parse(min_period).add(months=-3).last_of('quarter')
        else:
            period = pendulum.now().last_of("quarter")
        while period >= start_record_period:
            params.append({"period": period.format(str_format)})
            period = period.add(months=-3).last_of("quarter")
    else:
        max_f_ann_date = self.max("f_ann_date")
        if max_f_ann_date is not None:
            period = pendulum.parse(max_f_ann_date).add(days=1)
        else:
            period = start_record_period
        while period.diff(pendulum.now(), False).in_days() > 0:
            params.append({"f_ann_date": period.format(str_format)})
            period = period.add(days=1)
    return params


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params
