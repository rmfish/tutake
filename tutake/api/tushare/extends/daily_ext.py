import pendulum

from tutake.api.process_report import ProcessType


def default_cron_express_ext(self) -> str:
    return "0 1 * * *"


def default_order_by_ext(self) -> str:
    return "trade_date desc,ts_code"


def default_limit_ext(self):
    return '6000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    :return:
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    if ProcessType.INCREASE == process_type:  # 如果是新增数据，可以按照天来获取数据更加快
        max_date = self.max("trade_date")
        date_format = 'YYYYMMDD'
        if max_date:
            cnt = self.count(condition='trade_date=%s' % max_date)
            df = self.tushare_api().daily(trade_date=max_date)
            if df.shape[0] == cnt:
                stock_cnt = self.dao.stock_basic.count()
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
    return self.dao.stock_basic.column_data(['ts_code', 'list_date'])


def param_loop_process_ext(self, process_type: ProcessType, **params):
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
