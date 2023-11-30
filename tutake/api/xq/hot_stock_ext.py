"""
Xueqiu hot_stock接口
热门的股票ETF数据 热门类型（etf_query: 热门ETF, etf_1h:1小时热门ETF, etf_follow:热门关注ETF, stock_query:热门股票, stock_increase: 热门股票飙升, stock_comment:热评股票, stock_follow：热门关注股票, cube:热门组合）
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
    return [{"hot_type": "etf_query"}, {"hot_type": "etf_1h"}, {"hot_type": "etf_follow"}, {"hot_type": "stock_query"},
            {"hot_type": "stock_increase"}, {"hot_type": "stock_comment"}, {"hot_type": "stock_follow"},
            {"hot_type": "cube"}]


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    date = self.max('trade_date', f"hot_type='{params.get('hot_type')}'")
    if date == pendulum.now().format("YYYYMMDD"):
        return None
    return params
