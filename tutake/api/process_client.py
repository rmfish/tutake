import logging
import time
from collections.abc import Sequence
from functools import partial

from tutake.api.process import ProcessStatus
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.xq.xueqiu_api import XueQiuAPI
from tutake.utils.config import TutakeConfig


class Task(object):
    def __init__(self, _name, _type):
        self.name = _name
        self.type = _type

    def default_cron_express(self):
        return ''


class TushareProcessTask(object):
    def __init__(self, config: TutakeConfig):
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger

        self.timezone = config.get_config("tutake.scheduler.timezone", 'Asia/Shanghai')
        if config.get_config("tutake.scheduler.background", False):
            self._scheduler = BackgroundScheduler(timezone=self.timezone)
        else:
            self._scheduler = BlockingScheduler(timezone=self.timezone)
        self.logger = logging.getLogger("tutake.task")
        self.config = config
        self.started_cnt = 0

    def _api_schedule_config(self):
        """
        获取所有api的schedule配置
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
        check_cron = configs.get('check') or "30 0 * * 6"
        tasks = self._get_all_task()
        api_crontabs = []
        api_schedule = {'check_cron': check_cron, 'default_cron': default_cron, 'apis': api_crontabs}
        for task in tasks:
            cron = ""
            skip = False
            if task:
                cron = task.default_cron_express()
            if task.name in configs.keys():
                cron = configs.get(task.name)
                if cron is None:  # 配置cron为空的代表跳过不执行
                    skip = True
            elif task.type in configs.keys():
                cron = configs.get(task.type)
                if cron is None:  # 配置cron为空的代表跳过不执行
                    skip = True

            if cron is not None and cron != '':
                api_crontabs.append(
                    {'api': task.name, 'task': task, 'cron': cron, 'skip': skip, 'group': "seperator"})
            else:
                api_crontabs.append(
                    {'api': task.name, 'task': task, 'cron': default_cron, 'skip': skip, 'group': "default"})
        return api_schedule

    def _api_to_jobs(self, schedule_configs):
        """
        将api添加到任务中
        :return:
        """
        default_cron = schedule_configs.get('default_cron')
        check_cron = schedule_configs.get('check_cron')
        api_crontabs = schedule_configs.get('apis')
        default_crontabs = []
        check_jobs = []
        for cron in api_crontabs:
            check_jobs.append(cron['task'])
            if not cron["skip"]:
                if cron["group"] == 'default':
                    default_crontabs.append(cron['task'])
                else:
                    self.add_job(f"tutake_{cron['api']}", cron['task'],
                                 trigger=CronTrigger.from_crontab(cron['cron'], timezone=self.timezone))
        if len(default_crontabs) > 0:
            self.add_job("default_schedule", default_crontabs,
                         trigger=CronTrigger.from_crontab(default_cron, timezone=self.timezone))
        if len(check_jobs) > 0:
            self._scheduler.add_job(self._do_check, args=[check_jobs], id='check_schedule', name='check_schedule',
                                    trigger=CronTrigger.from_crontab(check_cron, timezone=self.timezone))

    def _get_all_task(self) -> [Task]:
        tushare_api = TushareAPI(self.config)
        xq_api = XueQiuAPI(self.config)
        apis = []
        for i in tushare_api.all_apis():
            apis.append(tushare_api.instance_from_name(i, self.config))
        for i in xq_api.all_apis():
            apis.append(xq_api.instance_from_name(i, self.config))
        return apis

    def _do_process(self, tasks, entrypoint="scheduler"):
        def __process(_job_id, _task) -> ProcessStatus:
            if _task is not None:
                return _task.process(entrypoint=entrypoint)
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

    def _do_check(self, tasks):
        def __check(_job_id, _task):
            if _task is not None:
                _task.check()

        start = time.time()
        status_cnt = 0
        if isinstance(tasks, Task):
            __check(f"tutake_{tasks.name}", tasks)
            status_cnt = 1
        elif isinstance(tasks, Sequence):
            for task in tasks:
                try:
                    __check(f"tutake_{task.name}", task)
                    status_cnt = status_cnt + 1
                except Exception as err:
                    # self.logger.error(f"Exception with {api} process,err is {err}")
                    continue
        self.logger.info(
            f"Finished {status_cnt} of check tasks, it takes {time.time() - start}s.")

    def get_scheduler(self):
        return self._scheduler

    def add_job(self, job_id, api, **kwargs):
        self._scheduler.add_job(self._do_process, args=[api], id=job_id, name=job_id, **kwargs)

    def start(self, now=False, check=False):
        try:
            schedule_configs = self._api_schedule_config()
            if now:
                tasks = [api['task'] for api in schedule_configs.get('apis') if not api['skip']]
                self._do_process(tasks, "manual")
            if check:
                tasks = [api['task'] for api in schedule_configs.get('apis')]
                self._do_check(tasks)
            self._api_to_jobs(schedule_configs)
            self._scheduler.start()
        except (Exception, KeyboardInterrupt) as err:
            self.logger.error(f"Exit with {type(err).__name__} {err}")


class TushareProcess(object):
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
