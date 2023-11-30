def default_order_by_ext(self) -> str:
    return "cal_date,exchange"


def default_limit_ext(self):
    return ''

    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{'exchange': 'SSE'}, {'exchange': 'SZSE'}, {'exchange': 'CFFEX'}, {'exchange': 'SHFE'},
            {'exchange': 'CZCE'}, {'exchange': 'DCE'}, {'exchange': 'INE'}]
