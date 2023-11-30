"""
Xueqiu index_valuation接口
指数估值
"""
import pendulum



def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return ''


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "100000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    max = self.max('trade_date')
    current = pendulum.now(tz="Asia/Shanghai").add(days=-1).format('YYYYMMDD')
    if current == max:
        return []
    return [{"date": current}]

