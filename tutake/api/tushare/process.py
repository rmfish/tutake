import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum

import pendulum
from pendulum import DateTime

from tutake.utils.config import tutake_config


class ProcessType(Enum):
    HISTORY = 1  # 同步历史数据
    INCREASE = 2  # 同步增量数据


class ProcessPercent(object):
    def __init__(self, total):
        self.total = total
        self.finished = 0

    def finish(self, cnt: int = 1):
        self.finished += cnt

    def percent(self):
        return self.finished / self.total

    def format(self):
        return '{}%'.format('%.2f' % (self.percent() * 100))


class ProcessException(Exception):
    def __init__(self, param: dict, cause: Exception):  # real signature unknown
        super().__init__(param, cause)
        self.param = param
        self.cause = cause


class ActionResult(object):

    def __init__(self, start, params, new_params=None, cnt: int = 0, err: Exception = None, status: str = 'Success'):
        self.start = start
        self.end = time.time()
        self.params = params
        self.new_params = new_params
        self.err = err
        self.status = status
        self.cnt = cnt

    def get_error(self):
        return self.err

    def get_params(self):
        return self.params

    def is_process_error(self):
        if self.err and isinstance(self.err, ProcessException):
            return True
        else:
            return False

    def __repr__(self):
        return "{}{} cnt:{} cost:{}s err:{}".format(self.status, self.new_params, self.cnt, self.end - self.start,
                                                    self.err)


class ProcessReport:
    def __init__(self, name, process_type: ProcessType, logger):
        self.percent = ProcessPercent(0)
        self.name = name
        self.process_type = process_type
        self.start_time: DateTime = pendulum.now()
        self.end_time: DateTime = pendulum.now()
        self.params = None
        self.task: [ActionResult] = []
        self._start()
        self.logger = logger
        self.total_task = 0
        self.repeat_task = 0

    def __str__(self):
        return '''
        Process: {} {}
        Time: {} ~ {}
        Cost: {}s
        TaskInfo: {}
        Params: {}
        ActionInfos: {}
        '''.format(self.name, self.process_type, self.start_time.format("YYYY-MM-DD HH:mm:ss"),
                   self.end_time.format("HH:mm:ss"),
                   self._cost_time(),
                   self._get_result_summary(),
                   self._get_params_summary(), self._get_action_summary())

    def _get_result_summary(self):
        run = len(self.task)
        records, success, skip, failed, repeat = 0, 0, 0, 0, 0
        for t in self.task:
            records += t.cnt
            if t.status == 'Success':
                success += 1
            elif t.status == 'Skip':
                skip += 1
            elif t.status == 'Failed':
                failed += 1
                if t.is_process_error():
                    repeat += 1
        return "{}/{} [Run:{} Success:{} Skip:{} Failed:{} Repeat:{}]".format(records, self.total_task, run, success,
                                                                              skip,
                                                                              failed,
                                                                              repeat)

    def _get_params_summary(self) -> str:
        if len(self.params) > 6:
            return "{}...{}".format(self.params[:2], self.params[-2:])

    def _get_action_summary(self) -> str:
        if len(self.task) > 6:
            _task = [t for t in self.task if t.status == 'Failed']
            if len(_task) > 4:
                return "{}...{}".format(_task[:2], _task[-2:])
            else:
                return "{}...{}".format(self.task[:2], self.task[-2:])

    def _start(self):
        self.start_time = pendulum.now()
        return self

    def close(self):
        self.end_time = pendulum.now()
        return self

    def _cost_time(self):
        return self.start_time.diff(self.end_time, abs=False).microseconds/1000000

    def set_exec_params(self, params, _type: str = "Normal"):
        if params:
            task_cnt = len(params)
            self.percent = ProcessPercent(task_cnt)
            if _type == 'Normal':
                self.total_task = task_cnt
                self.params = params
            elif _type == "Repeat":
                self.repeat_task = task_cnt
                self.total_task += task_cnt

    def get_process_percent(self) -> (float, str):
        return self.percent.percent(), self.percent.format()

    def finish_task(self, result: ActionResult) -> bool:
        self.task.append(result)
        self.percent.finish()
        if result.status == 'Skip':
            self.logger.debug("[{}] Skip exec param: {}".format(self.get_process_percent(), self.params))
        elif result.status == 'Failed':
            self.logger.error("Throw exception with param: {} err:{}".format(result.params, result.err))
        elif result.status == 'Success':
            self.logger.info(
                "[{}-{}] Fetch and append data, cnt is {} . param is {}".format(self.name,
                                                                                self.get_process_percent()[1],
                                                                                result.cnt, result.new_params))
        if result and result.err:
            if isinstance(result.err, ProcessException):
                return False
            elif isinstance(result.err, Exception):
                return True
        else:
            return False

    def repeat(self):
        params = [r.get_params() for r in self.task if r.is_process_error()]
        if params and len(params) > 0:
            self.name = "{}_r".format(self.name)
            return params
        return None


class DataProcess:

    def __init__(self, name):
        self.logger = logging.getLogger(('api.tushare.%s' % name))
        self.name = name

    def prepare(self, process_type: ProcessType):
        """
        同步历史数据准备工作
        """

    def tushare_parameters(self, process_type: ProcessType):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return [{}]

    def param_loop_process(self, process_type: ProcessType, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        return params

    def _process(self, process_type: ProcessType, fetch_and_append) -> ProcessReport:
        """
        同步历史数据
        :return:
        """
        report = ProcessReport(self.name, process_type, self.logger)
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        if params:
            report.set_exec_params(params)

            def action(param) -> ActionResult:
                start = time.time()
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    return ActionResult(start, param, new_param, status='Skip')
                try:
                    append_cnt = fetch_and_append(**new_param)
                    return ActionResult(start, param, new_param, append_cnt)
                except Exception as err:
                    if isinstance(err.args[0], str) and (err.args[0].startswith("抱歉，您没有访问该接口的权限")
                                                         or err.args[0].startswith("抱歉，您每天最多访问该接口")):
                        return ActionResult(start, param, new_param,
                                            err=Exception("Exit with tushare api flow limit. {}", err.args[0]),
                                            status='Failed')
                    else:
                        return ActionResult(start, param, new_param, err=ProcessException(param=new_param, cause=err),
                                            status='Failed')

            with ThreadPoolExecutor(max_workers=tutake_config.get_process_thread_cnt()) as pool:
                for result in pool.map(action, params):
                    if report.finish_task(result):
                        self.logger.critical("Stop with critical exception. {}", result)
                        return report

                repeat_params = report.repeat()
                if repeat_params:
                    report.set_exec_params(repeat_params, 'Repeat')
                    for p in repeat_params:
                        report.finish_task(action(p))
        return report.close()