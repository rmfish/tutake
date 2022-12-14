import pendulum


def default_cron_express_ext(self) -> str:
    return ""


from tutake.api.ts.index_basic import TushareIndexBasic


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '8000'


def prepare_ext(self):
    """
    同步历史数据准备工作
    """


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return self.api.index_basic.column_data(['ts_code', 'list_date'],
                                            TushareIndexBasic.market.not_in(['MSCI', 'CNI']),
                                            TushareIndexBasic.list_date.is_not(None))


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    date_format = 'YYYYMMDD'
    max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
    if max_date is None:
        params['start_date'] = ""
    elif max_date == pendulum.now().format(date_format):
        # 如果已经是最新时间
        return None
    else:
        max_date = pendulum.parse(max_date)
        start_date = max_date.add(days=1)
        params['start_date'] = start_date.format(date_format)
    return params
