def default_order_by_ext(self) -> str:
    return "in_date"


def default_limit_ext(self):
    return ''

    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{"hs_type": "SH"}, {"hs_type": "SZ"}]
