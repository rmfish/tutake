import pendulum
from apscheduler.triggers.cron import CronTrigger

from flask import Flask

from tutake.api.tushare.client import TushareProcessTask
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
        tasks = tutake_config.get_config("tutake.tasks")
        for task in tasks:
            for k, v in task.items():
                if k and v:
                    self.task.add_job(k, trigger=CronTrigger.from_crontab(v, timezone='Asia/Shanghai'))

    def start(self):
        self._config_schedule_tasks()
        self.scheduler.start()
        self.app.run()


if __name__ == '__main__':
    taskMgr = TaskManager()
    taskMgr.start()
