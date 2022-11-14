import pendulum

from flask import Flask

from tutake.api.tushare.client import TushareProcessTask
from tutake.task.scheduler import APScheduler


class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_ALLOWED_HOSTS = ["*"]


class TaskManager:

    def __init__(self):
        self.task = TushareProcessTask()
        self.app = Flask('Tutake data process task')
        self.app.config.from_object(Config())
        self.scheduler = APScheduler(self.task.get_scheduler())
        self.scheduler.init_app(self.app)

    def _config_schedule_tasks(self):
        time = pendulum.now().add(seconds=5)
        self.task.daily(trigger='cron', hour=time.hour, minute=time.minute, second=time.second)

    def start(self):
        self._config_schedule_tasks()
        self.scheduler.start()
        self.app.run()


if __name__ == '__main__':
    taskMgr = TaskManager()
    taskMgr.start()
