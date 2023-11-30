"""
Tushare hibor接口
Hibor利率,每日12点更新，HIBOR (Hongkong InterBank Offered Rate)，是香港银行同行业拆借利率。指香港货币市场上，银行与银行之间的一年期以下的短期资金借贷利率，从伦敦同业拆借利率（LIBOR）变化出来的。
数据接口-宏观经济-国内宏观-利率数据-Hibor利率  https://tushare.pro/document/2?doc_id=153
"""
from tutake.api.ts.date_utils import start_end_step_params


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'date desc'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return "4000"


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return start_end_step_params(self, '20021202', 4000, 'date')
