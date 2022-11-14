import json
import time
from enum import Enum

import pendulum
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc
from sqlalchemy.orm import sessionmaker, declarative_base

from tutake.utils.config import tutake_config
from tutake.utils.singleton import Singleton

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tutake.db'),
                       connect_args={"check_same_thread": False})
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TaskReport(Base):
    __tablename__ = "process_report"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, index=True, comment='job_id')
    name = Column(String, index=True, comment='任务名称')
    start_time = Column(String, index=True, comment='开始时间')
    end_time = Column(String, index=True, comment='结束时间')
    total_task = Column(Integer, comment='总任务数')
    repeat_task = Column(Integer, comment='重复执行任务数')
    status = Column(String, comment='任务状态')
    params = Column(String, comment='任务状态')
    task = Column(String, comment='任务状态')


TaskReport.__table__.create(bind=engine, checkfirst=True)


class ProcessType(str, Enum):
    HISTORY = 'HISTORY'  # 同步历史数据
    INCREASE = 'INCREASE'  # 同步增量数据


class ProcessPercent(object):
    def __init__(self, total):
        self.total = total
        self.finished = 0

    def finish(self, cnt: float = 1):
        self.finished += cnt

    def percent(self):
        if self.total is None or self.total == 0:
            return 0
        return self.finished / self.total

    def format(self):
        return '{}%'.format('%.2f' % (self.percent() * 100))


class ProcessException(Exception):
    def __init__(self, param: dict, cause: Exception):  # real signature unknown
        super().__init__(param, cause)
        self.param = param
        self.cause = cause


class ActionResult(object):

    def __init__(self, start, end, params, new_params=None, cnt: int = 0, err: Exception = None,
                 status: str = 'Success'):
        self.start = start
        self.end = end
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
    def __init__(self, _id, _name, _process_type: ProcessType, _logger):
        self.percent = ProcessPercent(0)
        self.name = _name
        self._id = _id
        self.process_type = _process_type
        self.start_time = pendulum.now()
        self.end_time = pendulum.now()
        self.params = None
        self.task: [ActionResult] = []
        self.logger = _logger
        self.total_task = 0
        self.repeat_task = 0
        self.status = 'Waiting'

    def get_id(self):
        return self._id

    def to_dict(self):
        result = self._get_result_summary()
        return {"id": self._id, "name": self.name, "process_type": self.process_type,
                "start_time": self.start_time.format("YYYY-MM-DD HH:mm:ss"),
                "end_time": self.end_time.format("YYYY-MM-DD HH:mm:ss"),
                "cost_second": self._cost_time(), "records": result[0],
                "api_invoke": result[1], "cnt_run": result[2], "cnt_success": result[3],
                "cnt_skip": result[4],
                "cnt_failed": result[5], "cnt_repeat": result[6], "params": self.params, "status": self.status,
                "process": self.percent.percent()
                }

    def __repr__(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __str__(self):
        result = self._get_result_summary()
        result_summary = "{}/{} [Run:{} Success:{} Skip:{} Failed:{} Repeat:{}]".format(result[0], result[1], result[2],
                                                                                        result[3], result[4], result[5],
                                                                                        result[6])
        return '''===ReportSummary===\nProcess: {} {}\nTime: {} ~ {}\nCost: {}s\nTaskInfo: {}\nParams: {}\nActionInfos: {}\n'''.format(
            self.name, self.process_type, self.start_time.format("YYYY-MM-DD HH:mm:ss"),
            self.end_time.format("HH:mm:ss"),
            self._cost_time(),
            result_summary,
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
        return records, self.total_task, run, success, skip, failed, repeat

    def _get_params_summary(self) -> str:
        if self.params is None:
            return "{}"
        if len(self.params) > 6:
            return "{}...{}".format(self.params[:2], self.params[-2:])

    def _get_action_summary(self) -> str:
        if self.task is None:
            return "{}"
        if len(self.task) > 6:
            _task = [t for t in self.task if t.status == 'Failed']
            if len(_task) > 4:
                return "{}...{}".format(_task[:2], _task[-2:])
            else:
                return "{}...{}".format(self.task[:2], self.task[-2:])

    def start(self):
        self.start_time = pendulum.now()
        self.status = 'RUNNING'
        return self

    def close(self):
        self.end_time = pendulum.now()
        self.status = 'SUCCESS'
        return self

    def _cost_time(self):
        period = self.start_time.diff(self.end_time, abs=False)
        return period.in_seconds() + period.microseconds / 1000000

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
                self.status = 'CRITICAL_FAILED'
                return True
        else:
            return False

    def repeat(self):
        params = [r.get_params() for r in self.task if r.is_process_error()]
        if params and len(params) > 0:
            self.name = "{}_r".format(self.name)
            self.status = 'FAILED_OVER_RUNNING'
            return params
        return None


@Singleton
class ProcessReportContainer(object):
    def __init__(self):
        self.running_reports = dict()

    def _add_report(self, report: ProcessReport):
        reports = self.running_reports.get(report.get_id())
        if reports is None:
            self.running_reports[report.get_id()] = [report]
        else:
            reports.append(report)

    def _remove_report(self, report: ProcessReport):
        reports = self.running_reports.get(report.get_id())
        if reports:
            reports.remove(report)

    def create_process_report(self, _id, name, process_type: ProcessType, logger):
        report = ProcessReport(_id, name, process_type, logger)
        self._add_report(report)
        report.start()
        return report

    def get_reports(self, job_id, status, page=0, page_size=20):
        if status == 'RUNNING':
            return self.running_reports.get(job_id)
        if page_size:
            page_size = int(page_size)
        session = session_factory()
        rows = session.query(TaskReport).filter_by(job_id=job_id).order_by(desc(TaskReport.start_time)).limit(
            page_size).offset(int(page) * page_size).all()
        reports = []

        for r in rows:
            obj = r.__dict__
            task_report = ProcessReport(obj.get('job_id'), obj.get('name'), obj.get('process_type'), None)
            task_report.repeat_task = obj.get('repeat_task')
            task_report.total_task = obj.get('total_task')
            task_report.status = obj.get('status')
            task_report.start_time = pendulum.parse(obj.get('start_time'))
            task_report.end_time = pendulum.parse(obj.get('end_time'))
            task_report.percent = ProcessPercent(1)
            task_report.percent.finish(1)
            task_report.params = json.loads(obj.get('params'))
            task_report.task = [ActionResult(**t)
                                for t in json.loads(obj.get('task'))]
            reports.append(task_report)
        mem_report = self.running_reports.get(job_id)
        if mem_report:
            reports.extend(mem_report)
        reports.sort(key=lambda x: x.start_time, reverse=True)
        return reports

    def save_report(self, report: ProcessReport):
        if report:
            task_report = TaskReport()
            task_report.job_id = report.get_id()
            task_report.name = report.name
            task_report.process_type = report.process_type
            task_report.total_task = report.total_task
            task_report.repeat_task = report.repeat_task
            task_report.status = report.status
            task_report.start_time = str(report.start_time)
            task_report.end_time = str(report.end_time)
            task_report.params = json.dumps(report.params)
            task_report.task = json.dumps(report.task, default=lambda x: x.__dict__)
            session = session_factory()
            session.add(task_report)
            session.commit()
            self._remove_report(report)
