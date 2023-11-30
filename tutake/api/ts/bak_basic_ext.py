"""
获取备用基础列表，数据从2016年开始
"""


def default_order_by_ext(self) -> str:
    return "trade_date,ts_code"


def default_limit_ext(self):
    return '5000'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    import pendulum
    _start_day = pendulum.parse('20160101')
    params = []
    _max_date = self.max('trade_date', condition="trade_date != ''")
    if _max_date is None:
        _max_date = _start_day
    else:
        _max_date = pendulum.parse(_max_date).add(days=1)
    while _max_date > pendulum.now():
        params.append({'trade_date': _max_date.format("YYYYMMDD")})
        _max_date = _max_date.add(days=1)
    return params
