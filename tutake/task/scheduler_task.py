from apscheduler.triggers.cron import CronTrigger
from flask import Flask

from tutake.api.tushare.client import TushareProcessTask
from tutake.api.tushare.dao import DAO
from tutake.task.scheduler import APScheduler
from tutake.utils.config import tutake_config


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_ALLOWED_HOSTS = ["*"]
    SCHEDULER_API_PREFIX = '/api'


class TaskManager:

    def __init__(self):
        self.task = TushareProcessTask()
        self.app = Flask('Tutake data process task')
        self.app.config.from_object(Config())
        self.scheduler = APScheduler(self.task.get_scheduler())
        self.scheduler.init_app(self.app)
        self.dao = DAO()

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
        config_tasks = tutake_config.get_config("tutake.schedule.tasks")
        # default_cron = tutake_config.get_config("tutake.schedule.default_cron", "37 20 * * *")
        timezone = tutake_config.get_config("tutake.schedule.timezone", 'Asia/Shanghai')
        configs = {}
        for i in config_tasks:
            configs = {**configs, **i}
        default_cron = configs.get('default')
        if not default_cron:
            default_cron = "10 0,6,21 * * *"
        apis = self.dao.all_apis()
        default_schedule = []
        for api in apis:
            api_instance = self.dao.instance_from_name(api)
            cron = ""
            if api_instance:
                cron = api_instance.default_cron_express()
            if configs.get(api):
                cron = configs.get(api)
            if cron:
                self.task.add_job(f"tushare_{api}", api, trigger=CronTrigger.from_crontab(cron, timezone=timezone))
            else:
                default_schedule.append(api)
        if len(default_schedule) > 0:
            self.task.add_job("default_schedule", default_schedule,
                              trigger=CronTrigger.from_crontab(default_cron, timezone=timezone))

    def start(self):
        self._config_schedule_tasks()
        self.scheduler.start()
        self.app.run()


if __name__ == '__main__':
    taskMgr = TaskManager()
    taskMgr.start()
