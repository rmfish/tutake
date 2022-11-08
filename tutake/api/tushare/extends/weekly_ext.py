from tutake.api.tushare.process import ProcessType


def default_limit_ext(self):
    return '4500'


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
    return self.dao.stock_basic.column_data(['ts_code', 'list_date'])


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    from datetime import datetime, timedelta
    date_format = '%Y%m%d'
    if process_type == ProcessType.HISTORY:
        min_date = self.min("trade_date",
                            "ts_code = '%s'" % params['ts_code'])
        if min_date is None:
            params['end_date'] = ""
        else:
            min_date = datetime.strptime(min_date, date_format)
            end_date = min_date - timedelta(days=7)
            if params.get('list_date'):
                list_date = datetime.strptime(params.get('list_date'),
                                              date_format)
                interval = (end_date - list_date).days
                if interval < 0:
                    return None
            params['end_date'] = end_date.strftime(date_format)
        return params
    else:
        max_date = self.max("trade_date",
                            "ts_code = '%s'" % params['ts_code'])
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
