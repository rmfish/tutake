from tutake.api.process_client import TushareProcess, TushareProcessTask
from tutake.api.query_client import TushareQuery, XueQiuQuery
from tutake.utils.config import TutakeConfig


class Tutake(object):
    def __init__(self, config_file_path=None):
        self.config = TutakeConfig(config_file_path)
        self._ts = None
        self._xq = None
        self._task = None
        self._process = None

    def tushare_api(self):
        if not self._ts:
            self._ts = TushareQuery(self.config)
        return self._ts

    def xueqiu_api(self):
        if not self._xq:
            self._xq = XueQiuQuery(self.config)
        return self._xq

    def task_api(self):
        if not self._task:
            self._task = TushareProcessTask(self.config)
        return self._task

    def process_api(self):
        if not self._process:
            self._process = TushareProcess(self.config)
        return self._process
