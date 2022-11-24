import pendulum

from tutake.api.process_report import ProcessType


def default_cron_express_ext(self) -> str:
    return ""


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date desc,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '3000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """


def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    000016.SH,上证50
    000905.SH,中证500
    399001.SZ,深证成指
    399005.SZ,中小板指
    399006.SZ,创业板指
    399905.SZ,中证500
    """
    codes = ['000001.SH', '000005.SH', '000006.SH', '000016.SH', '000300.SH', '000905.SH', '399001.SZ', '399005.SZ',
             '399006.SZ', '399016.SZ', '399300.SZ', '399905.SZ']
    return [{'ts_code': i} for i in codes]


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    date_format = 'YYYYMMDD'
    if process_type == ProcessType.HISTORY:
        min_date = self.min("trade_date", "ts_code = '%s'" % params['ts_code'])
        if min_date is None:
            params['end_date'] = ""
        elif params.get('list_date') == min_date:
            # 如果时间相等不用执行
            return None
        else:
            min_date = pendulum.parse(min_date)
            end_date = min_date.add(days=-1)
            params['end_date'] = end_date.format(date_format)
        return params
    else:
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
