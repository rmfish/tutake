import logging
import time
from concurrent.futures import ThreadPoolExecutor

from ordered_enum import OrderedEnum

from tutake.api.base_dao import BatchWriter, Records

percent_logger = logging.getLogger('tutake.process.percent')
task_logger = logging.getLogger('tutake.process.task')


class ProcessException(Exception):
    def __init__(self, param: dict, cause: Exception):  # real signature unknown
        super().__init__(param, cause)
        self.param = param
        self.cause = cause


class CriticalException(Exception):
    def __init__(self, msg: str, cause: Exception = None):  # real signature unknown
        super().__init__(msg, cause)
        self.msg = msg
        self.cause = cause


class ProcessPercent(object):
    def __init__(self, total):
        self.total = total
        self.finished = 0
        self.step = 2
        self.step_percent = 0

    def finish(self, cnt: float = 1):
        self.finished += cnt

    def percent(self):
        if self.total is None or self.total == 0:
            return 0
        return self.finished / self.total

    def is_step_percent(self):
        if self.percent() >= self.step_percent / 100:
            self.step_percent += self.step
            return True
        else:
            return False

    def format(self):
        return '{}%'.format('%.2f' % (self.percent() * 100))


class ProcessStatusEnum(OrderedEnum):
    PENDING = 1
    SKIP = 2
    FAILED = 3
    SUCCESS = 4
    RUNNING = 5


class ProcessTask:
    def __init__(self, input_params):
        self.input_params = input_params
        self.run_params = None
        self.status = ProcessStatusEnum.PENDING
        self.records = None
        self.err = None
        if input_params is not None and input_params.get("RETRY_TAG") is not None:
            self.retry = True
        else:
            self.retry = False

    def start(self, run_params):
        self.run_params = run_params
        return self

    def stop(self, status=ProcessStatusEnum.SUCCESS, records=None, err=None):
        self.status = status
        self.records = records
        self.err = err
        if err is not None:
            self.status = ProcessStatusEnum.FAILED
        return self

    def records_cnt(self):
        if self.records is None:
            return 0
        elif isinstance(self.records, Records):
            return self.records.size()
        else:
            return self.records

    def is_success(self):
        return self.status == ProcessStatusEnum.SUCCESS

    def is_critical_failed(self):
        if self.err:
            if isinstance(self.err, ProcessException):
                return isinstance(self.err.cause, CriticalException)
            elif isinstance(self.err, Exception):
                self.status = ProcessStatusEnum.FAILED
                return True
        else:
            return False

    def retry_params(self):
        self.input_params["RETRY_TAG"] = True
        return self.input_params

    def is_retry(self):
        return self.retry

    def is_skip(self):
        return self.status == ProcessStatusEnum.SKIP

    def is_failed(self):
        return self.status == ProcessStatusEnum.FAILED


class ProcessStatus:
    def __init__(self, name, params):
        self.params = params
        self.name = name
        self.task_cnt = 0
        self.retry_cnt = 0
        self.skip = 0
        self.failed = 0
        self.records_cnt = 0
        self.break_down = False
        self.percent = ProcessPercent(len(params))
        self.run_time = 0

    def run_once(self, task: ProcessTask):
        if task.is_retry():
            self.retry_cnt = self.retry_cnt + 1
        elif task.is_failed():
            self.failed = self.failed + 1
        elif task.is_skip():
            self.skip = self.skip + 1
        else:
            self.task_cnt = self.task_cnt + 1
        self.records_cnt = self.records_cnt + task.records_cnt()
        self.percent.finish()
        if self.percent.is_step_percent():
            percent_logger.debug(
                f"({self.name}-{self.percent.format()}) Fetch and append data, cnt is {self.records_cnt}")

    def format_run_time(self):
        return '%.4f' % self.run_time

    def _run_cnt(self):
        return self.task_cnt + self.skip + self.failed + self.retry_cnt

    def status(self):
        total_cnt = len(self.params)
        if self.break_down:
            return ProcessStatusEnum.FAILED
        if total_cnt > 0:
            if self._run_cnt() == 0:
                return ProcessStatusEnum.PENDING
            if self.task_cnt + self.skip + self.failed < total_cnt:
                return ProcessStatusEnum.RUNNING
        return ProcessStatusEnum.SUCCESS

    def __str__(self):
        return f"{self.name} [{self.status().name}] {self.records_cnt}/{len(self.params)} [T{(self._run_cnt())}/S{self.task_cnt}/K{self.skip}/F{self.failed}/R{self.retry_cnt}] [{self.format_run_time()}s]"

    def __repr__(self):
        return self.__str__()


class DataProcess:
    """
    获取保存数据的核心类，用以实现获取数据到保存数据的过程，封装了中间的限流、异常、重试、日志、多线程等的一些处理步骤，每个具体的接口都继承这个类，
    在每个具体的实现类中实现获取数据和保存的具体操作
    """

    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.max_repeat = config.get_config("tutake.process.max_repeat", 1000)
        self.forbidden_config = config.get_process_forbidden()

    def name(self):
        return self.name

    def process(self, **kwargs) -> ProcessStatus:
        pass

    def api_token_limit(self) -> (int, int):
        """
        接口的限制
        :return: （最小的积分，接口限流）
        """
        return ()

    def prepare(self):
        """
        同步历史数据准备工作
        """

    def query_parameters(self):
        """
        同步历史数据调用的参数
        :return: list(dict)
        """
        return [{}]

    def param_loop_process(self, **params):
        """
        每执行一次fetch_and_append前，做一次参数的处理，如果返回None就中断这次执行
        """
        return params

    def _forbidden_entrypoint(self, entrypoint):
        if entrypoint is None:
            entrypoint = "main"
        if self.forbidden_config.get(entrypoint):
            return self.name in self.forbidden_config.get(entrypoint)
        return False

    def _process(self, fetch_and_append, writer: BatchWriter = None, **kwargs) -> ProcessStatus:
        """
        同步历史数据
        :return:
        """
        entrypoint = kwargs.get("entrypoint")
        if self._forbidden_entrypoint(entrypoint):
            task_logger.warning(f"Ignore process {self.name()}. forbidden by {entrypoint} entrypoint")
            return ProcessStatus(self.name, [])

        start = time.time()
        self.prepare()
        params = self.query_parameters()
        status = ProcessStatus(self.name, params)
        try:
            writer.start()
            status = self._inner_process(params, fetch_and_append, status, writer)
            status.run_time = time.time() - start
            if status.break_down:
                writer.rollback()
            else:
                writer.commit()
                task_logger.debug(
                    f"Finished {self.entities.__name__} process. run {status.task_cnt} tasks, save {status.records_cnt} records,takes {status.format_run_time()}s")
        except Exception as err:
            logging.exception(err)
        return status

    def _inner_process(self, process_params, fetch_and_append, status: ProcessStatus, writer: BatchWriter = None,
                       retry_cnt=0):
        if retry_cnt > self.max_repeat:
            # TODO
            status.break_down = True
            # self.logger.error(f"Over max retry cnt. {self.name} {status.err}")
            return status
        elif retry_cnt > 0:
            task_logger.warning(
                f"Start the {retry_cnt}'s retry {self.entities.__name__} process, retry tasks cnt is {len(process_params)}")
        else:
            task_logger.warning(
                f"Start the {self.entities.__name__} process, tasks cnt is {len(process_params)}")

        if process_params:
            def action(param) -> ProcessTask:
                task = ProcessTask(param)
                new_param = self.param_loop_process(**param)
                task.start(new_param)
                if new_param is None:
                    return task.stop(ProcessStatusEnum.SKIP)
                try:
                    records = fetch_and_append(**new_param)
                    return task.stop(records=records)
                except Exception as err:
                    return task.stop(err=err)

            retry_params = []
            with ThreadPoolExecutor(max_workers=self.config.get_process_thread_cnt()) as pool:
                for result in pool.map(action, process_params):
                    status.run_once(result)
                    if result.is_success():
                        writer.add_records(result.records)
                    elif result.is_skip():
                        continue
                    elif result.is_critical_failed():
                        status.break_down = True
                        task_logger.critical(f"Stop with critical exception. {result}")
                        return
                    else:
                        retry_params.append(result.retry_params())

            if len(retry_params) > 0:
                status_name = status.name
                if retry_cnt == 0:
                    status_name = status_name + "-R"
                retry_status = ProcessStatus(status_name, retry_params)
                retry_status = self._inner_process(retry_params, fetch_and_append, retry_status, writer, retry_cnt + 1)
                if retry_status.break_down:
                    status.break_down = True
        return status
