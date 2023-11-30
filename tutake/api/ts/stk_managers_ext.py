from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    return "ann_date desc,ts_code"


def default_limit_ext(self):
    return '4000'

    # self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, start_date='20191221', step=30, date_col='ann_date')
