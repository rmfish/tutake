def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    return "trade_date,ts_code"


def default_limit_ext(self):
    return '4500'


def prepare_ext(self):
    """
    同步历史数据准备工作
    :return:
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return self.api.stock_basic.column_data(['ts_code', 'list_date'])


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    from datetime import datetime, timedelta
    date_format = '%Y%m%d'
    max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
    if max_date is None:
        params['start_date'] = ""
    else:
        max_date = datetime.strptime(max_date, date_format)
        start_date = max_date + timedelta(days=7)
        if params.get('list_date'):
            if (start_date - datetime.now()).days > 0:
                return None
            else:
                params['start_date'] = start_date.strftime(date_format)
    return params
