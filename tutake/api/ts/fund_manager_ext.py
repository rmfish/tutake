"""
Tushare fund_manager接口
获取公募基金经理数据，包括基金经理简历等数据
数据接口-公募基金-基金经理  https://tushare.pro/document/2?doc_id=208
"""

from tutake.api.ts.date_utils import day_by_day_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'ts_code,ann_date desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "50000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    cnt = self.count()
    if cnt > 0:
        return day_by_day_params(self, "20000222", "ann_date")
    else:
        return [{}]
