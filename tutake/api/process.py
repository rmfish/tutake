import logging
import time
from concurrent.futures import ThreadPoolExecutor

from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, TimeElapsedColumn, Task, SpinnerColumn, \
    MofNCompleteColumn, ProgressColumn
from rich.text import Text

from tutake.api.process_report import ProcessReport, ProcessType, ActionResult, ProcessException, ProcessReportContainer


class TaskCntColumn(ProgressColumn):

    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__()

    def render(self, task: "Task") -> Text:
        record_cnt = task.fields.get(self.field_name)
        if record_cnt is None:
            return Text("0", style="progress.data.speed")
        return Text(f"{record_cnt}", style="progress.data.speed")


process_bar = Progress(TextColumn("[progress.description]{task.description}"), SpinnerColumn(), BarColumn(),
                       MofNCompleteColumn(),
                       TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), TimeRemainingColumn(),
                       TimeElapsedColumn(), TaskCntColumn('record_cnt'), TaskCntColumn('success_cnt'),
                       TaskCntColumn('skip_cnt'), TaskCntColumn('failed_cnt'))


class DataProcess:

    def __init__(self, name, config):
        self.logger = logging.getLogger('api.tushare.%s' % name)
        self.name = name
        self._report_container = ProcessReportContainer(config)
        self.config = config

    def name(self):
        return self.name

    def process(self, process_type: ProcessType = ProcessType.INCREASE):
        pass

    def default_cron_express(self) -> str:
        return ""

    def api_token_limit(self) -> (int, int):
        """
        接口的限制
        :return: （最小的积分，接口限流）
        """
        return ()

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
        # self.logger.info(f"Start {self.entities.__name__} {process_type} process.")
        report = self._report_container.create_process_report("tushare_%s" % self.name, self.name, process_type,
                                                              self.logger)
        self.prepare(process_type)
        params = self.tushare_parameters(process_type)
        if params:
            report.set_exec_params(params)

            def action(param) -> ActionResult:
                start = time.time()
                new_param = self.param_loop_process(process_type, **param)
                if new_param is None:
                    return ActionResult(start, time.time(), param, new_param, status='Skip')
                try:
                    append_cnt = fetch_and_append(**new_param)
                    return ActionResult(start, time.time(), param, new_param, append_cnt)
                except ProcessException as err:
                    return ActionResult(start, time.time(), {**param, **err.param}, new_param, err=err, status='Failed')
                except Exception as err:
                    return ActionResult(start, time.time(), param, new_param,
                                        err=ProcessException(param=new_param, cause=err), status='Failed')

            task_id = process_bar.add_task(description=self.name, total=len(params))
            with ThreadPoolExecutor(max_workers=self.config.get_process_thread_cnt()) as pool:
                for result in pool.map(action, params):
                    process_bar.advance(task_id, 1)
                    critical_failed = report.finish_task(result)
                    process_bar.update(task_id, **report.result_summary())
                    if critical_failed:
                        process_bar.stop_task(task_id)
                        self.logger.critical("Stop with critical exception. {}", result)
                        return report

                repeat_params = report.repeat()
                while repeat_params and len(repeat_params) > 0:
                    process_bar.update(task_id, description=self.name + "[R]", completed=0, total=len(repeat_params))
                    report.set_exec_params(repeat_params, 'Repeat')
                    for result in pool.map(action, repeat_params):
                        process_bar.advance(task_id, 1)
                        report.finish_task(result)
                        process_bar.update(task_id, **report.result_summary())
                    repeat_params = report.repeat()
        report = report.close()
        # self.logger.info(f"Finished {self.entities.__name__} {process_type} process. it takes {report.process_time()}s")
        return report
