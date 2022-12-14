import logging
import os.path
import time
from collections.abc import Sequence
from datetime import datetime, timedelta
from functools import partial

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from tutake.api.process import DataProcess
from tutake.api.process_bar import process
from tutake.api.process_report import ProcessReportContainer, ProcessType, ProcessReport
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.xq.xueqiu_api import XueQiuAPI
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import file_dir


def process_api(config_path):
    config = __config_from_file(config_path)
    if not config:
        raise Exception(f"Config file {config_path} is not exists, pls check it.")
    return TushareProcessTask(config)


def task_api(config_path):
    config = __config_from_file(config_path)
    if not config:
        raise Exception(f"Config file {config_path} is not exists, pls check it.")
    return TushareProcessTask(config)


def __config_from_file(config_file_path):
    if not os.path.exists(config_file_path):
        return None
    return TutakeConfig(file_dir(config_file_path), os.path.basename(config_file_path))


class TushareProcessTask:
    def __init__(self, config: TutakeConfig):
        self.timezone = config.get_config("tutake.scheduler.timezone", 'Asia/Shanghai')
        if config.get_config("tutake.scheduler.background", False):
            self._scheduler = BackgroundScheduler(timezone=self.timezone)
        else:
            self._scheduler = BlockingScheduler(timezone=self.timezone)
        self.report_container = ProcessReportContainer(config)
        self.logger = logging.getLogger("tutake.task")
        self.config = config
        self.started_cnt = 0

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
        apis = self._get_all_api()
        default_schedule = []
        for api in apis:
            cron = ""
            if api:
                cron = api.default_cron_express()
            if api.name in configs.keys():
                cron = configs.get(api.name)
                if cron is None:  # 配置cron为空的代表跳过不执行
                    continue
            if cron:
                self.add_job(f"tutake_{api.name}", api, trigger=CronTrigger.from_crontab(cron, timezone=self.timezone))
            else:
                default_schedule.append(api)
        if len(default_schedule) > 0:
            self.add_job("default_schedule", default_schedule,
                         trigger=CronTrigger.from_crontab(default_cron, timezone=self.timezone))

    def _get_all_api(self):
        tushare_api = TushareAPI(self.config)
        xq_api = XueQiuAPI(self.config)
        apis = []
        for i in tushare_api.all_apis():
            apis.append(tushare_api.instance_from_name(i, self.config))
        for i in xq_api.all_apis():
            apis.append(xq_api.instance_from_name(i, self.config))
        return apis

    def _finish_task_report(self, job_id, report: ProcessReport):
        self.report_container.save_report(report)

    def _do_process(self, apis, process_type: ProcessType = ProcessType.INCREASE):
        def __process(_job_id, _api):
            if _api is not None:
                report = _api.process(process_type)
                self._finish_task_report(_job_id, report)
                return report
            else:
                return None

        start = time.time()
        reports = []
        self._start_process()
        if isinstance(apis, DataProcess):
            reports.append(__process(f"tutake_{apis.name}", apis))
        elif isinstance(apis, Sequence):
            for api in apis:
                try:
                    reports.append(__process(f"tutake_{api.name}", api))
                except Exception as err:
                    # self.logger.error(f"Exception with {api} process,err is {err}")
                    continue
        self._end_process()
        process.console.log(f"Finished {len(reports)} of scheduled tasks, it takes {time.time() - start}s")
        if reports:
            process.console.log("Process results summary:")
            for r in reports:
                if r:
                    process.console.log(f"{r.name} {r.process_summary_str()}  cost {r.process_time()}s")

    def _start_process(self):
        self.started_cnt += 1
        process.start()

    def _end_process(self):
        self.started_cnt -= 1
        if self.started_cnt == 0:
            process.stop()

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

    def start(self, now=False):
        try:
            self._config_schedule_tasks()
            if now:
                high_priority_job = [job for job in self._scheduler.get_jobs() if job.id != 'default_schedule']
                default_job = [job for job in self._scheduler.get_jobs() if job.id == 'default_schedule']
                for job in high_priority_job:
                    job.modify(next_run_time=datetime.now())
                for job in default_job:
                    job.modify(next_run_time=datetime.now() + timedelta(seconds=5))
            self._scheduler.start()
        except (Exception, KeyboardInterrupt) as err:
            self.logger.error(f"Exit with {type(err).__name__} {err}")

    def __getattr__(self, name):
        return partial(self.add_job, name)


class TushareProcess:
    def __init__(self, config: TutakeConfig):
        self.api = TushareAPI(config)
        self.config = config

    def process(self, api_name, process_type: ProcessType = ProcessType.INCREASE):
        api = self.api.__getattr__(api_name)
        if api is not None:
            return api.process(process_type)
        else:
            return None

    def __getattr__(self, name):
        return partial(self.process, name)
