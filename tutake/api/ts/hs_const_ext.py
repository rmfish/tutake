def default_order_by_ext(self) -> str:
    return "in_date"


def default_limit_ext(self):
    return ''


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{"hs_type": "SH"}, {"hs_type": "SZ"}]

def need_to_process_ext(self, **kwargs):
    from tutake.api.ts.date_utils import min_count_and_last_process
    return min_count_and_last_process(self, last_process_day=30)


def prepare_write_ext(self, writer, **kwargs):
    """
    同步历史数据准备工作
    """
    self.delete_all()