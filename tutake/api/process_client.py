import logging
import time
from collections.abc import Sequence
from datetime import datetime, timedelta
from functools import partial

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from tutake.api.process import ProcessStatus
# from tutake.api.process_report import ProcessReportContainer, ProcessReport
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.xq.xueqiu_api import XueQiuAPI
from tutake.utils.config import TutakeConfig


class Task(object):
    def __init__(self, _name, _type):
        self.name = _name
        self.type = _type

    def default_cron_express(self):
        return ''


class TushareProcessTask:
    def __init__(self, config: TutakeConfig):
        self.timezone = config.get_config("tutake.scheduler.timezone", 'Asia/Shanghai')
        if config.get_config("tutake.scheduler.background", False):
            self._scheduler = BackgroundScheduler(timezone=self.timezone)
        else:
            self._scheduler = BlockingScheduler(timezone=self.timezone)
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
        tasks = self._get_all_task()
        default_schedule = []
        for task in tasks:
            cron = ""
            if task:
                cron = task.default_cron_express()
            if task.name in configs.keys():
                cron = configs.get(task.name)
                if cron is None:  # 配置cron为空的代表跳过不执行
                    continue
            elif task.type in configs.keys():
                cron = configs.get(task.type)
                if cron is None:  # 配置cron为空的代表跳过不执行
                    continue

            if cron:
                self.add_job(f"tutake_{task.name}", task,
                             trigger=CronTrigger.from_crontab(cron, timezone=self.timezone))
            else:
                default_schedule.append(task)
        if len(default_schedule) > 0:
            self.add_job("default_schedule", default_schedule,
                         trigger=CronTrigger.from_crontab(default_cron, timezone=self.timezone))

    def _get_all_task(self) -> [Task]:
        tushare_api = TushareAPI(self.config)
        xq_api = XueQiuAPI(self.config)
        apis = []
        for i in tushare_api.all_apis():
            apis.append(tushare_api.instance_from_name(i, self.config))
        for i in xq_api.all_apis():
            apis.append(xq_api.instance_from_name(i, self.config))
        return apis

    # def _finish_task_report(self, job_id, report: ProcessReport):
    # self.report_container.save_report(report)

    def _do_process(self, tasks):
        def __process(_job_id, _task) -> ProcessStatus:
            if _task is not None:
                return _task.process()
            else:
                return None

        start = time.time()
        status_list = []
        if isinstance(tasks, Task):
            status_list.append(__process(f"tutake_{tasks.name}", tasks))
        elif isinstance(tasks, Sequence):
            for task in tasks:
                try:
                    status_list.append(__process(f"tutake_{task.name}", task))
                except Exception as err:
                    # self.logger.error(f"Exception with {api} process,err is {err}")
                    continue
        if status_list:
            status_list = [x for x in status_list if x is not None]
            status_list.sort(key=lambda x: (x.status(), x.name))
            result = '\n|-'.join([str(x) for x in status_list])
            self.logger.info(
                f"Finished {len(status_list)} of scheduled tasks, it takes {time.time() - start}s. Tasks details is:\n|-{result}")

    def get_scheduler(self):
        return self._scheduler

    def add_job(self, job_id, api, **kwargs):
        self._scheduler.add_job(self._do_process, args=[api], id=job_id, name=job_id, **kwargs)

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

    # def __getattr__(self, name):
    #     return partial(self.add_job, name)


class TushareProcess:
    def __init__(self, config: TutakeConfig):
        self.api = TushareAPI(config)
        self.config = config

    def process(self, api_name):
        api = self.api.__getattr__(api_name)
        if api is not None:
            return api.process()
        else:
            return None

    def __getattr__(self, name):
        return partial(self.process, name)
