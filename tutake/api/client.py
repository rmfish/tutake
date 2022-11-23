import logging
import time
from collections.abc import Sequence
from functools import partial

import tushare
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from tutake.api.process_report import ProcessReportContainer, ProcessType, ProcessReport
from tutake.api.tushare.dao import DAO
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


def pro_api(token='', data_dir: str = None):
    config = TutakeConfig()
    config.set_tushare_token(token)
    config.set_tutake_data_dir(data_dir)
    return TushareQuery(config)


def process_api(config: TutakeConfig):
    return TushareProcess(config)


def task_api(config: TutakeConfig):
    return TushareProcessTask(config)


class TushareProcessTask:
    def __init__(self, config: TutakeConfig):
        self.timezone = config.get_config("tutake.scheduler.timezone", 'Asia/Shanghai')
        self.dao = DAO()
        if config.get_config("tutake.scheduler.background", False):
            self._scheduler = BackgroundScheduler(timezone=self.timezone)
        else:
            self._scheduler = BlockingScheduler(timezone=self.timezone)
        self.report_container = ProcessReportContainer(config)
        self.logger = logging.getLogger("tutake.task")
        self.config = config

    def _config_schedule_tasks(self):
        """
            *    *    *    *    *
            -    -    -    -    -
            |    |    |    |    |
            |    |    |    |    +----- day of week (0 - 7) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
            |    |    |    +---------- month (1 - 12) OR jan,feb,mar,apr ...
            |    |    +--------------- day of month (1 - 31)
            |    +-------------------- hour (0 - 23)
            +------------------------- minute (0 - 59)
        :return:
        """
        config_tasks = self.config.get_config("tutake.scheduler.tasks", [])
        configs = {}
        for i in config_tasks:
            configs = {**configs, **i}
        default_cron = configs.get('default') or "10 0,6,21 * * *"
        apis = self.dao.all_apis()
        default_schedule = []
        for api in apis:
            api_instance = self.dao.instance_from_name(api, self.config)
            cron = ""
            if api_instance:
                cron = api_instance.default_cron_express()
            if configs.get(api):
                cron = configs.get(api)
            if cron:
                self.add_job(f"tushare_{api}", api, trigger=CronTrigger.from_crontab(cron, timezone=self.timezone))
            else:
                default_schedule.append(api)
        if len(default_schedule) > 0:
            self.add_job("default_schedule", default_schedule,
                         trigger=CronTrigger.from_crontab(default_cron, timezone=self.timezone))

    def _finish_task_report(self, job_id, report: ProcessReport):
        self.report_container.save_report(report)

    def _do_process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        def __process(_job_id, __name):
            api = self.dao.__getattr__(__name, self.config)
            if api is not None:
                report = api.process(process_type)
                self._finish_task_report(_job_id, report)
                return report
            else:
                return None

        if isinstance(api_name, str):
            report = __process(f"tushare_{api_name}", api_name)
            self.logger.info(f"Finish {api_name} process,report is \n {report}")
        elif isinstance(api_name, Sequence):
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

    def start(self):
        try:
            self._config_schedule_tasks()
            self._scheduler.start()
        except (Exception, KeyboardInterrupt) as err:
            self.logger.error(f"Exit with {type(err).__name__} {err}")

    def __getattr__(self, name):
        return partial(self.add_job, name)


class TushareProcess:
    def __init__(self, config: TutakeConfig):
        self.dao = DAO()
        self.config = config

    def process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        api = self.dao.__getattr__(api_name, self.config)
        if api is not None:
            return api.process(process_type)
        else:
            return None

    def __getattr__(self, name):
        return partial(self.process, name)


class TushareQuery:
    def __init__(self, config):
        token = config.get_tushare_token()
        if token != '':
            self.tushare = tushare.pro_api(token)
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
    # dao = pro_api("aec595052cb10051350a6a164f41b344b922f0b3ee206efdec2e0082")
    # print(dao.stock_basic(fields='name,ts_code,', name='ST国华'))
    # print(dao.shibor(start_date='20180101', end_date='20181101'))

    task = task_api(TutakeConfig(project_root()))
    task.start()
