

def default_cron_express_ext(self) -> str:
    return "10 0 1 * *"


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
    import pendulum
    date_format = 'YYYYMMDD'
    max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
    if max_date is None:
        params['start_date'] = ""
    else:
        start_date = pendulum.parse(max_date).add(months=1)
        if params.get('list_date'):
            if start_date.to_date_string()[:-2] > pendulum.now().to_date_string()[:-2]:
                return None
            if start_date.diff(pendulum.now(), abs=False).days < 0:
                return None
            else:
                params['start_date'] = start_date.format(date_format)
    return params
