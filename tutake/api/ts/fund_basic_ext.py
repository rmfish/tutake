def default_order_by_ext(self) -> str:
    return "found_date desc,ts_code"


def default_limit_ext(self):
    return '15000'


def prepare_write_ext(self, writer, **kwargs):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{"market": "E"}, {"market": "O"}]
