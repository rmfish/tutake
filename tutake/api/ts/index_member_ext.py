def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'index_code,con_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '3000'


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
    # return self.api.index_classify.column_data(['index_code'])
    return [{}]

def need_to_process_ext(self, **kwargs):
    from tutake.api.ts.date_utils import min_count_and_last_process
    return min_count_and_last_process(self, last_process_day=30)