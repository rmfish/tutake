import pendulum


def daily_params_loop(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    from datetime import datetime, timedelta
    date_format = '%Y%m%d'
    if params.get("ts_code"):
        max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
        if max_date is None:
            params['start_date'] = ""
        elif max_date == datetime.now().strftime(date_format):
            # 如果已经是最新时间
            return None
        else:
            max_date = datetime.strptime(max_date, date_format)
            start_date = max_date + timedelta(days=1)
            params['start_date'] = start_date.strftime(date_format)
        return params
    else:
        return params


def day_by_day_params(self, start_date, date_column="ann_date"):
    params = []
    start_date = pendulum.parse(start_date)
    end_date = pendulum.now()
    max_date = self.max(date_column)
    if max_date:
        max_date = pendulum.parse(max_date)
    else:
        max_date = start_date
    while max_date.diff(end_date, abs=False).days > 0:
        max_date = max_date.add(days=1)
        params.append({date_column: max_date.format("YYYYMMDD")})
    return params


def m_by_m_params(self, start_date, end_of_month=True, date_column="trade_date"):
    params = []
    start_date = pendulum.parse(start_date)
    end_date = pendulum.now()
    max_date = self.max(date_column)
    if max_date:
        max_date = pendulum.parse(max_date)
    else:
        max_date = start_date
    while max_date.diff(end_date, abs=False).days > 0:
        max_date = max_date.add(months=1)
        if end_of_month:
            max_date = max_date.last_of("month")
        else:
            max_date = max_date.start_of("month")
        params.append({date_column: max_date.format("YYYYMMDD")})
    return params


def q_by_q_params(self, start_date, date_column="ann_date"):
    params = []
    start_date = pendulum.parse(start_date)
    end_date = pendulum.now()
    max_date = self.max(date_column)
    if max_date:
        max_date = pendulum.parse(max_date)
    else:
        max_date = start_date
    while max_date.diff(end_date, abs=False).days > 0:
        max_date = max_date.add(days=1)
        params.append({date_column: max_date.format("YYYYMMDD")})
    return params


def start_end_step_params(self, start_date: str = "19990104", step=7, date_col='trade_date'):
    date_format = 'YYYYMMDD'
    start_date = pendulum.parse(start_date)
    dates = []
    max_date = self.max(date_col)
    if max_date:
        start_date = pendulum.parse(max_date).add(days=1)
    while start_date <= pendulum.now():
        end_date = start_date.add(days=step)
        dates.append(
            {"start_date": start_date.format(date_format), "end_date": end_date.format(date_format)})
        start_date = end_date.add(days=1)
    return dates


def quarter_params(self, start_period: str = "19901231", date_col="f_ann_date", query_period_col=None):
    """
    基于财报的相关数据，主要使用end_date（财报季），f_ann_date（发表日）数据查询相关的数据
    :param date_col:
    :param start_period: 最早的财报季
    :param query_period_col: 查询报告期字段
    :param self:
    :return:
    """
    params = []
    str_format = "YYYYMMDD"
    start_record_period = pendulum.parse(start_period)  # 最早的数据记录
    max_period = self.max(date_col)
    if query_period_col is None:
        query_period_col = date_col
    if max_period is None or pendulum.now().diff(
            pendulum.parse(max_period), abs=False).in_months() > 3:
        min_period = self.min("end_date", condition="end_date is not null")
        if min_period is not None:
            period = pendulum.parse(min_period).add(months=-3).last_of('quarter')
        else:
            period = pendulum.now().last_of("quarter")
        while period >= start_record_period:
            params.append({"period": period.format(str_format)})
            period = period.add(months=-3).last_of("quarter")
    else:
        if max_period is not None:
            period = pendulum.parse(max_period).add(months=3)
        else:
            period = start_record_period
        while period.diff(pendulum.now(), False).in_days() > 0:
            params.append({query_period_col: period.format(str_format)})
            period = period.add(months=3)
    return params


def get_latest_quarter(self):
    last_quarter_day = pendulum.now().last_of("quarter").add(months=-3).last_of("quarter")
    return last_quarter_day.format("YYYYMMDD")
