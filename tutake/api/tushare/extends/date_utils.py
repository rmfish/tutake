import pendulum

from tutake.api.process_report import ProcessType


def financial_report_time_params(self, process_type: ProcessType, start_period: str = "19901231"):
    """
    基于财报的相关数据，主要使用end_date（财报季），f_ann_date（发表日）数据查询相关的数据
    :param start_period: 最早的财报季
    :param self:
    :param process_type:
    :return:
    """
    params = []
    str_format = "YYYYMMDD"
    start_record_period = pendulum.parse(start_period)  # 最早的数据记录
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
