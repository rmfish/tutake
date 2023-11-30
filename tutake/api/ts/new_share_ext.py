def default_order_by_ext(self) -> str:
    return "ipo_date desc,ts_code"


def default_limit_ext(self):
    return '2000'

    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
