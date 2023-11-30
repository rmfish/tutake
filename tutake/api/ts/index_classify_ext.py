def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'index_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return ''


def prepare_ext(self):
    """
    同步历史数据准备工作
    """
    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
