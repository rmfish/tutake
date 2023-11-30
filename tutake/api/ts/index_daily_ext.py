import pandas as pd
import pendulum

from tutake.api.base_dao import checker_logger

from tutake.api.ts.index_basic import TushareIndexBasic


def default_order_by_ext(self) -> str:
    """
    查询时默认的排序
    """
    return 'trade_date,ts_code'


def default_limit_ext(self) -> str:
    """
    每次取数的默认Limit
    """
    return '8000'


def query_parameters_ext(self):
    """
    同步历史数据调用的参数
    :return: list(dict)
    """
    return self.api.index_basic.column_data(['ts_code', 'list_date'],
                                            TushareIndexBasic.market.not_in(['MSCI']),
                                            TushareIndexBasic.list_date.is_not(None))


def param_loop_process_ext(self, **params):
    """
    每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
    """
    date_format = 'YYYYMMDD'
    max_date = self.max("trade_date", "ts_code = '%s'" % params['ts_code'])
    if max_date is None:
        params['start_date'] = ""
    elif max_date == pendulum.now().format(date_format):
        # 如果已经是最新时间
        return None
    else:
        max_date = pendulum.parse(max_date)
        start_date = max_date.add(days=1)
        params['start_date'] = start_date.format(date_format)
    return params


def check_ext(self, **kwargs):
    indexes = pd.DataFrame(self.api.index_basic.column_data(['ts_code', 'list_date']))
    force_start = kwargs.get("force_start")
    if force_start is not None:
        start = force_start
    else:
        point = self.checker.check_point()
        if point[0] is not None:
            start = point[0].get('list_date')
        else:
            start = None
    if start is not None:
        indexes = indexes[(indexes['list_date'] >= start) & (indexes['list_date'].notnull())]
    else:
        indexes = indexes[indexes['list_date'].notnull()]
    indexes = indexes.sort_values('list_date', ignore_index=True)
    count = 0
    for idx, row in indexes.iterrows():
        tushare = self.fetch_and_append(ts_code=row['ts_code'])
        db = self.index_daily(ts_code=row['ts_code'], limit=100000)
        if tushare.size() != db.shape[0]:
            tushare_pd = set(pd.DataFrame(tushare.items, columns=tushare.fields)['trade_date'].unique().tolist())
            db_pd = set(db['trade_date'].unique().tolist())
            diff = list(tushare_pd - db_pd)
            if len(diff) == 0:
                diff = list(db_pd - tushare_pd)
            if len(diff) == 0:
                duplicates = db.duplicated('trade_date')
                print(db[duplicates])
            checker_logger.warning(
                f"Not equals data. The date is {row['ts_code']}. tushare size is {tushare.size()}, db size is {db.shape[0]}, diff is {diff}")
            if force_start is None and row['list_date'] is not None:
                self.checker.error_point(list_date=row['list_date'])
            return
        if count % 30 == 0:
            checker_logger.warning(f"Start check time of {row['list_date']}")
            if row['list_date'] is not None:
                self.checker.save_point(list_date=row['list_date'])
        count = count + 1
