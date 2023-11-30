from datetime import datetime, timedelta


def default_order_by_ext(self) -> str:
    return "cal_date,exchange"


def default_limit_ext(self):
    return ''


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{'exchange': 'SSE'}, {'exchange': 'SZSE'}, {'exchange': 'CFFEX'}, {'exchange': 'SHFE'},
            {'exchange': 'CZCE'}, {'exchange': 'DCE'}, {'exchange': 'INE'}]


def need_to_process_ext(self, **kwargs):
    """
    同步历史数据准备工作
    """
    max_date = self.max("cal_date")
    if max_date is not None:
        return max_date < (datetime.now() + timedelta(days=-31)).strftime("%Y%m")
    return True


def prepare_write_ext(self, writer, **kwargs) -> bool:
    self.delete_all()
