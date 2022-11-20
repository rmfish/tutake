import pendulum

from tutake.api.process_report import ProcessType


def daily_params(self, process_type: ProcessType, entity_cnt_func, default_params_func, step=2):
    if ProcessType.INCREASE == process_type:  # 如果是新增数据，可以按照天来获取数据更加快
        max_date = self.max("trade_date")
        date_format = 'YYYYMMDD'
        if max_date:
            cnt = self.count(condition='trade_date=%s' % max_date)
            df = self.tushare_query(self.name, fields='', trade_date=max_date)
            if df.shape[0] == cnt:
                stock_cnt = entity_cnt_func(process_type)
                start_date = pendulum.parse(max_date)
                if pendulum.now().diff(start_date).days / 3 < stock_cnt:
                    dates = []
                    start_date = start_date.add(days=1)
                    while start_date <= pendulum.now():
                        end_date = start_date.add(days=2)
                        dates.append(
                            {"start_date": start_date.format(date_format), "end_date": end_date.format(date_format)})
                        start_date = end_date.add(days=1)
                    return dates
    return default_params_func(process_type)


def daily_params_loop(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    from datetime import datetime, timedelta
    date_format = '%Y%m%d'
    if params.get("ts_code"):
        if process_type == ProcessType.HISTORY:
            min_date = self.min("trade_date", "ts_code = '%s'" % params['ts_code'])
            if min_date is None:
                params['end_date'] = ""
            elif params.get('list_date') == min_date:
                # 如果时间相等不用执行
                return None
            else:
                min_date = datetime.strptime(min_date, date_format)
                end_date = min_date - timedelta(days=1)
                params['end_date'] = end_date.strftime(date_format)
            return params
        else:
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


def day_by_day_params(self, process_type: ProcessType, start_date, date_column="ann_date"):
    params = []
    start_date = pendulum.parse(start_date)
    if process_type == ProcessType.HISTORY:
        min_date = self.min(date_column)
        if min_date:
            min_date = pendulum.parse(min_date)
        else:
            min_date = pendulum.now()
        while min_date.diff(start_date, abs=False).days < 0:
            min_date = min_date.add(days=-1)
            params.append({date_column: min_date.format("YYYYMMDD")})
    else:
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


def q_by_q_params(self, process_type: ProcessType, start_date, date_column="ann_date"):
    params = []
    start_date = pendulum.parse(start_date)
    if process_type == ProcessType.HISTORY:
        min_date = self.min(date_column)
        if min_date:
            min_date = pendulum.parse(min_date)
        else:
            min_date = pendulum.now()
        while min_date.diff(start_date, abs=False).days < 0:
            min_date = min_date.add(days=-1)
            params.append({date_column: min_date.format("YYYYMMDD")})
    else:
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


def start_end_step_params(self, process_type: ProcessType, start_date: str = "19990104", step=7):
    date_format = 'YYYYMMDD'
    start_date = pendulum.parse(start_date)
    dates = []
    if ProcessType.INCREASE == process_type:  # 如果是新增数据，可以按照天来获取数据更加快
        max_date = self.max("trade_date")
        if max_date:
            start_date = pendulum.parse(max_date).add(days=1)
        while start_date <= pendulum.now():
            end_date = start_date.add(days=step)
            dates.append(
                {"start_date": start_date.format(date_format), "end_date": end_date.format(date_format)})
            start_date = end_date.add(days=1)
        return dates
    else:
        min_date = self.min("trade_date")
        if min_date:
            end_date = pendulum.parse(min_date).add(days=-1)
            while end_date >= start_date:
                start_date = end_date.add(days=-step)
                dates.append(
                    {"start_date": start_date.format(date_format), "end_date": end_date.format(date_format)})
                end_date = start_date.add(days=-1)
            return dates


def quarter_params(self, process_type: ProcessType, start_period: str = "19901231"):
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
