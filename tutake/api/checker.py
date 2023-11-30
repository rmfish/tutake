import pandas as pd
import pendulum

from tutake.api.base_dao import TutakeCheckerPoint, checker_logger, BatchWriter


def _auto_data_repair(self, trade_date, ts_codes):
    writer = BatchWriter(self.engine, self.table_name)
    if len(ts_codes) < 100:
        for ts_code in ts_codes:
            checker_logger.info(f"Auto fix {self.name} data of {ts_code}")
            checker_logger.info(
                self._process_by_func(lambda: self.delete_by(ts_code=ts_code), lambda: [{"ts_code": ts_code}],
                                      self.fetch_and_append, writer))
    else:
        checker_logger.info(f"Auto fix {self.name} data of {trade_date}")
        checker_logger.info(
            self._process_by_func(lambda: self.delete_by(trade_date=trade_date), lambda: [{"trade_date": trade_date}],
                                  self.fetch_and_append, writer))


def check_by_date(self, method, default_start, force_start=None, date_apply=lambda d: d.add(days=1), print_step=30,
                  diff_column='ts_code',
                  diff_repair=_auto_data_repair):
    """
    一个按照日期进行检测的通用函数，
    :param self:
    :param method: api获取数据的方法，一般为同名函数
    :param default_start: 默认第一个数据的起始值
    :param force_start:  强制从一个值开始检测
    :param date_apply: 计算日期的函数
    :param print_step: 打印的步进
    :param diff_column: 对比差异的列名
    :param diff_repair: 处理差异数据
    :return:
    """
    if force_start is not None:
        start_date = pendulum.parse(force_start)
    else:
        check_points = self.checker.check_point()
        if check_points[0] is None:
            start_date = default_start
        else:
            start_date = check_points[0].get("trade_date")
        start_date = pendulum.parse(start_date)
        if check_points[1]:
            start_date = date_apply(start_date)
    end_date = pendulum.now()
    checker_logger.warning(f"Start {self.name} checker. {start_date}")
    count = 0
    while start_date <= end_date:
        trade_date = start_date.format("YYYYMMDD")
        tushare = self.fetch_and_append(trade_date=trade_date)
        db = method(fields=diff_column, trade_date=trade_date, limit=1000000)
        if tushare.size() != db.shape[0]:
            tushare_pd = pd.DataFrame(tushare.items, columns=tushare.fields)
            diff = list(set(tushare_pd[diff_column].unique().tolist()) - set(db[diff_column].unique().tolist()))
            if diff_repair is not None:
                diff_repair(self, trade_date, diff)
                continue
            else:
                checker_logger.warning(
                    f"Not equals data. The date is {trade_date}. tushare size is {tushare.size()}, db size is {db.shape[0]}, diff is {diff}")
                if force_start is None:
                    self.checker.error_point(trade_date=trade_date)
            return
        if count % print_step == 0:
            checker_logger.warning(f"Start {self.name} check: {trade_date}")
            if force_start is None:
                self.checker.save_point(trade_date=trade_date)
        start_date = date_apply(start_date)
        count = count + 1
    if force_start is None:
        self.checker.save_point(trade_date=start_date.format("YYYYMMDD"))
