def default_order_by_ext(self) -> str:
    return "ts_code"


def default_limit_ext(self):
    return ''

    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{"list_status": "L"}, {"list_status": "D"}, {"list_status": "P"}]
