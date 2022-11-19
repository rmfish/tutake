from tutake.api.tushare.process import ProcessType


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'ts_code,code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '3000'


def prepare_ext(self, process_type: ProcessType):
    """
    同步历史数据准备工作
    """
    self.delete_all()

def tushare_parameters_ext(self, process_type: ProcessType):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return self.dao.ths_index.column_data(['ts_code'])


def param_loop_process_ext(self, process_type: ProcessType, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    return params