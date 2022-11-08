import logging
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep


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

    def _process(self, process_type: ProcessType, fetch_and_append):
        """
        同步历史数据
        :return:
        """
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        self.logger.debug("Process tushare params is {}".format(params))
        if params:
            percent = ProcessPercent(len(params))

            def action(param):
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    self.logger.debug("[{}] Skip exec param: {}".format(percent.format(), param))
                    return
                try:
                    cnt = fetch_and_append(**new_param)
                    self.logger.info("[{}] Fetch and append {} data, cnt is {} . param is {}".format(
                        percent.format(), self.name, cnt, param))
                except Exception as err:
                    if isinstance(err.args[0], str) and (err.args[0].startswith("抱歉，您没有访问该接口的权限")
                                                         or err.args[0].startswith("抱歉，您每天最多访问该接口")):
                        self.logger.error("Throw exception with param: {} err:{}".format(new_param, err))
                        raise Exception("Exit with tushare api flow limit. {}", err.args[0])
                    else:
                        self.logger.error("Execute fetch_and_append throw exp. {}".format(err))
                        return ProcessException(param=new_param, cause=err)

            with ThreadPoolExecutor(max_workers=tutake_config.get_process_thread_cnt()) as pool:
                repeat_params = []
                for result in pool.map(action, params):
                    percent.finish()
                    if isinstance(result, ProcessException):
                        repeat_params.append(result.param)
                    elif isinstance(result, Exception):
                        return
                # 过程中出现错误的，需要补偿执行
                cnt = len(repeat_params)
                if cnt > 0:
                    percent = ProcessPercent(cnt)
                    self.logger.warning(
                        "Failed process with exception.Cnt {}  All params is {}".format(cnt, repeat_params))
                    for p in repeat_params:
                        action(p)
                        percent.finish()
