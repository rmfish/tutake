import collections
import logging
import time
from functools import partial

import tushare as ts
from apscheduler.schedulers.background import BackgroundScheduler

from tutake.api.process_report import ProcessReportContainer, ProcessType, ProcessReport
from tutake.api.tushare.dao import DAO
from tutake.utils.config import tutake_config


def pro_api(token='', data_dir: str = None):
    return TushareQuery(token, data_dir)


def process_api(config: dict = None):
    return TushareProcess(config)


def task_api(config: dict = None):
    return TushareProcessTask(config)


# class TushareTaskHistory(object):
#
#     def __init__(self, job_id):
#         self.job_id = job_id
#         self.result: [ProcessReport] = []
#
#     def add_report(self, report: ProcessReport):
#         self.result.append(report)
#
#     def to_json(self):
#         return [i.to_dict() for i in self.result]


class TushareProcessTask:
    def __init__(self, _config: dict = None):
        tutake_config.merge_config(_config)
        self.dao = DAO()
        self._scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self.report_container = ProcessReportContainer()
        self.logger = logging.getLogger("tutake.task")

    def _finish_task_report(self, job_id, report: ProcessReport):
        self.report_container.save_report(report)
        # task = self._task_history.get(job_id)
        # if task is None:
        #     task = TushareTaskHistory(job_id)
        #     self._task_history[job_id] = task
        # task.add_report(report)

    def _do_process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        def __process(_job_id, __name):
            api = self.dao.__getattr__(__name)
            if api is not None:
                report = api.process(process_type)
                self._finish_task_report(_job_id, report)
                return report
            else:
                return None

        if isinstance(api_name, str):
            report = __process(f"tushare_{api_name}", api_name)
            self.logger.info(f"Finish {api_name} process,report is \n {report}")
        elif isinstance(api_name, collections.Sequence):
            reports = []
            start = time.time()
            self.logger.info(f"Start Schedule task with apis {api_name}")
            for api in api_name:
                try:
                    report = __process(f"tushare_{api}", api)
                    reports.append(report)
                    self.logger.info(f"Finish {api} process,report is \n {report}")
                except Exception as err:
                    self.logger.error(f"Exception with {api} process,err is {err}")
                    continue
            self.logger.info(f"Finished {len(api_name)} of scheduled tasks, it takes {time.time() - start}s")
            if reports:
                self.logger.info("Process results summary:")
                for r in reports:
                    self.logger.info(f"{r.name} {r.process_result()}  cost {r.process_time()}s")

    def get_scheduler(self):
        return self._scheduler

    def get_results(self, job_id) -> [ProcessReport]:
        return self.report_container.get_reports(job_id)

    def add_job(self, job_id, api_name, **kwargs):
        if kwargs.get('process_type'):
            args = [api_name, kwargs.get('process_type')]
        else:
            args = [api_name]
        self._scheduler.add_job(self._do_process, args=args, id=job_id, name=job_id, **kwargs)

    def __getattr__(self, name):
        return partial(self.add_job, name)


class TushareProcess:
    def __init__(self, _config: dict = None):
        tutake_config.merge_config(_config)
        self.dao = DAO()

    def process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        api = self.dao.__getattr__(api_name)
        if api is not None:
            return api.process(process_type)
        else:
            return None

    def __getattr__(self, name):
        return partial(self.process, name)


class TushareQuery:
    def __init__(self, tushare_token, data_dir: str = None):
        if tushare_token != '':
            self.tushare = ts.pro_api(tushare_token)
        if data_dir is not None:
            tutake_config.set_tutake_data_dir(data_dir)
        self.dao = DAO()

    def query(self, api_name, fields='', **kwargs):
        api = self.dao.__getattr__(api_name)
        if api is None:
            return self.fail_over(api_name, fields, **kwargs)
        method = getattr(api, api_name)
        if method is not None:
            return method(fields, **kwargs)
        return None

    def fail_over(self, api_name, fields='', **kwargs):
        if self.tushare is not None:
            return self.tushare.query(api_name, fields, **kwargs)

    def __getattr__(self, name):
        return partial(self.query, name)


if __name__ == "__main__":
    dao = pro_api("aec595052cb10051350a6a164f41b344b922f0b3ee206efdec2e0082")
    # print(dao.stock_basic(fields='name,ts_code,', name='ST国华'))
    print(dao.shibor(start_date='20180101', end_date='20181101'))
