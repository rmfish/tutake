"""
Tushare cn_cpi接口
获取CPI居民消费价格数据，包括全国、城市和农村的数据
数据接口-宏观经济-国内宏观-价格指数-居民消费价格指数（CPI）  https://tushare.pro/document/2?doc_id=228
"""
from datetime import datetime, timedelta


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'month desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "5000"


def need_to_process_ext(self, **kwargs):
    """
    同步历史数据准备工作
    """
    max_date = self.max("month")
    if max_date is not None:
        from datetime import datetime
        from datetime import timedelta
        return max_date < (datetime.now() + timedelta(days=-31)).strftime("%Y%m")
    return True


def prepare_write_ext(self, writer, **kwargs):
    self.delete_all()


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return [{}]
