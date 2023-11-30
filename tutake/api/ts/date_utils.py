import pendulum


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


def start_end_step_params(self, start_date: str = "19990104", step=7, date_col='trade_date'):
    """
    Build the start_date to end_date params array with day step. e.g.
    [{"start_date":"20130101","end_date":"20130201"},{"start_date":"20130201","end_date":"20130301"}]
    The duration of from start_date to end_date is config by the input param of 'step'
    The actual start_date is determined by start_date param and the time saved in database. If it exists in the database
    use the max value plus one day as the start_date,else use the input param of 'start_data'
    :param self:
    :param start_date: start date
    :param step: step of day
    :param date_col: the time col name in database
    :return:
    """
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
    """
    
    :param self:
    :return:
    """
    last_quarter_day = pendulum.now().last_of("quarter").add(months=-3).last_of("quarter")
    return last_quarter_day.format("YYYYMMDD")


def min_count_and_last_process(self, min_cnt=0, last_process_day=31):
    db_cnt = self.count()
    if db_cnt > min_cnt:
        point = self.checker.process_point()
        if point is not None and point[1] is not None:
            from datetime import datetime
            if (datetime.now() - point[1]).days < last_process_day:
                return False
    return True


def diff_in_units(datetime1, datetime2, timeunit):
    # 计算两个日期之间的差值
    delta = datetime2.diff(datetime1)

    # 检查所需的时间单位并返回相应的差值
    if timeunit == 'year':
        # 在同一个年份内，返回0
        if datetime1.year == datetime2.year:
            return 0
        else:
            return delta.in_years()
    elif timeunit == 'quarter':
        # 在同一个季度内，且在同一年内，返回0
        if datetime1.quarter == datetime2.quarter and datetime1.year == datetime2.year:
            return 0
        else:
            years_diff = datetime2.year - datetime1.year
            # 计算季度差
            quarters_diff = datetime2.quarter - datetime1.quarter
            # 计算总的季度差
            total_quarters_diff = years_diff * 4 + quarters_diff
            return total_quarters_diff
    elif timeunit == 'month':
        # 在同一个月份内，且在同一年内，返回0
        if datetime1.month == datetime2.month and datetime1.year == datetime2.year:
            return 0
        else:
            # 计算月份差，包括跨年
            month_diff = (datetime2.year - datetime1.year) * 12 + (datetime2.month - datetime1.month)
            return month_diff
    elif timeunit == 'week':
        # 在同一个周内，且在同一年内，返回0
        if datetime1.week_of_year == datetime2.week_of_year and datetime1.year == datetime2.year:
            return 0
        else:
            return delta.in_weeks()
    elif timeunit == 'day':
        return delta.in_days()
    else:
        raise ValueError(f"Invalid time unit: {timeunit}")


if __name__ == '__main__':
    date1 = pendulum.datetime(2020, 1, 1)
    date2 = pendulum.datetime(2021, 1, 1)
    date3 = pendulum.datetime(2021, 2, 1)
    date4 = pendulum.datetime(2021, 2, 28)
    date5 = pendulum.datetime(2021, 3, 1)
    date6 = pendulum.datetime(2022, 1, 1)
    date7 = pendulum.datetime(2022, 1, 31)
    date8 = pendulum.datetime(2022, 2, 1)

    # 测试月份差
    assert diff_in_units(date1, date2, 'month') == 12
    assert diff_in_units(date2, date1, 'month') == -12
    assert diff_in_units(date1, date1, 'month') == 0
    assert diff_in_units(date3, date4, 'month') == 0
    assert diff_in_units(date4, date5, 'month') == 1
    assert diff_in_units(date6, date7, 'month') == 0
    assert diff_in_units(date7, date8, 'month') == 1
