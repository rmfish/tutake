import json
import logging
import uuid

import pendulum
from sqlalchemy import create_engine, Column, Integer, String, desc
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import Base


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

    def __init__(self, _id, _name, _logger):
        self.percent = ProcessPercent(0)
        self.original_name = _name
        self.name = _name
        self._id = _id
        self.start_time = pendulum.now()
        self.end_time = pendulum.now()
        self.params = None
        self.task: [ActionResult] = []
        self.logger = _logger
        self.total_task = 0
        self.repeat_task = 0
        self.repeat_cnt = 0
        self.status = 'Waiting'

    def get_id(self):
        return self._id

    def to_dict(self):
        result = self.result_summary()
        return {"id": self._id, "name": self.name,
                "start_time": self.start_time.format("YYYY-MM-DD HH:mm:ss"),
                "end_time": self.end_time.format("YYYY-MM-DD HH:mm:ss"),
                "cost_second": self.process_time(), "records": result[0],
                "api_invoke": result['record_cnt'], "cnt_run": result['task_cnt'], "cnt_success": result['success_cnt'],
                "cnt_skip": result['skip_cnt'],
                "cnt_failed": result['failed_cnt'], "cnt_repeat": result['repeat_cnt'], "params": self.params,
                "status": self.status,
                "process": self.percent.percent()
                }

    def __repr__(self):
        return json.dumps(self.to_dict(), sort_keys=True)

    def __str__(self):
        return '''===ReportSummary===\nProcess: {} \nTime: {} ~ {}\nCost: {}s\nTaskInfo: {}\nParams: {}\nActionInfos: {}\n'''.format(
            self.name, self.start_time.format("YYYY-MM-DD HH:mm:ss"),
            self.end_time.format("HH:mm:ss"),
            self.process_time(),
            self.process_summary_str(),
            self._get_params_summary(), self._get_action_summary())

    def process_summary_str(self):
        result = self.result_summary()
        return f"{result['record_cnt']}/{result['task_cnt']} [Run:{result['run_cnt']} Success:{result['success_cnt']} Skip:{result['skip_cnt']} Failed:{result['failed_cnt']} Repeat:{result['repeat_cnt']}]"

    def result_summary(self):
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
        return {"record_cnt": records, "task_cnt": self.total_task, "run_cnt": run, "success_cnt": success,
                "skip_cnt": skip, "failed_cnt": failed, "repeat_cnt": repeat}

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

    def close(self, status='SUCCESS'):
        self.end_time = pendulum.now()
        self.status = status
        return self

    def process_time(self):
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
        if "uuid" in result.params.keys():
            for i, n in enumerate(self.task):
                if result.params.get('uuid') and n.params.get("uuid"):
                    self.task[i] = result
        else:
            self.task.append(result)
        self.percent.finish()
        if self.logger:
            # if result.status == 'Skip':
            #     if len(self.params) > 10:
            #         self.logger.log(
            #             "[{}] Skip exec param: {} and {} more".format(self.get_process_percent(), self.params[:10],
            #                                                           len(self.params)))
            #     else:
            #         self.logger.log("[{}] Skip exec param: {}".format(self.get_process_percent(), self.params))
            if result.status == 'Failed':
                self.logger.log(f"{self.name} Throw exception with param: {result.params} err:{result.err}")
                # self.logger.error("Throw exception with param: {} err:{}".format(result.params, result.err))
            elif result.status == 'Success':
                if self.percent.is_step_percent():
                    self.logger.log(
                        f"({self.name}-{self.get_process_percent()[1]}) Fetch and append data, cnt is {result.cnt} param is {result.new_params}")
                    # self.logger.info("[{}-{}] Fetch and append data, cnt is {} . param is {}".format(self.name,
                    #                                                                                  self.get_process_percent()[
                    #                                                                                      1],
                    #                                                                                  result.cnt,
                    #                                                                                  result.new_params))
                # else:
                #     self.logger.debug("[{}-{}] Fetch and append data, cnt is {} . param is {}".format(self.name,
                #                                                                                       self.get_process_percent()[
                #                                                                                           1],
                #                                                                                       result.cnt,
                #                                                                                       result.new_params))
        if result and result.err:
            if isinstance(result.err, ProcessException):
                return isinstance(result.err.cause, CriticalException)
            elif isinstance(result.err, Exception):
                self.status = 'CRITICAL_FAILED'
                return True
        else:
            return False

    def repeat(self):
        params = [r.get_params() for r in self.task if r.is_process_error()]
        if params and len(params) > 0:
            self.repeat_cnt += 1
            self.name = f"{self.original_name}_r[{self.repeat_cnt}]"
            self.status = 'FAILED_OVER_RUNNING'
            for p in params:
                p["uuid"] = uuid.uuid1()
            return params
        return None


class ProcessReportContainer(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.config = config
        self.running_reports = dict()
        engine = create_engine(config.get_data_sqlite_driver_url('tutake.db'),
                               connect_args={"check_same_thread": False})
        self.session_factory = sessionmaker()
        self.session_factory.configure(bind=engine)
        TaskReport.__table__.create(bind=engine, checkfirst=True)

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

    def create_process_report(self, _id, name, logger) -> ProcessReport:
        report = ProcessReport(_id, name, logger)
        self._add_report(report)
        report.start()
        return report

    def get_reports(self, job_id, status=None, page=0, page_size=20):
        if status == 'RUNNING':
            return self.running_reports.get(job_id)
        if page_size:
            page_size = int(page_size)

        session = self.session_factory()
        rows = session.query(TaskReport).filter_by(job_id=job_id).order_by(desc(TaskReport.start_time)).limit(
            page_size).offset(int(page) * page_size).all()
        reports = []

        for r in rows:
            obj = r.__dict__
            task_report = ProcessReport(obj.get('job_id'), obj.get('name'), None)
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
            task_report.total_task = report.total_task
            task_report.repeat_task = report.repeat_task
            task_report.status = report.status
            task_report.start_time = str(report.start_time)
            task_report.end_time = str(report.end_time)
            task_report.params = json.dumps(report.params)
            task_report.task = json.dumps(report.task, default=lambda x: x.__dict__)
            session = self.session_factory()
            session.add(task_report)
            session.commit()
            self._remove_report(report)
