# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from collections import OrderedDict

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from flask import current_app, request, Response
from .json_ext import jsonify
from ..api.process_report import ProcessReportContainer
from ..code.tushare_api import TushareJsonApi


def get_scheduler_info():
    """Gets the scheduler info."""

    scheduler = current_app.apscheduler

    d = OrderedDict([
        ('current_host', scheduler.host_name),
        ('allowed_hosts', scheduler.allowed_hosts),
        ('running', scheduler.running)
    ])

    return jsonify(d)


def add_job():
    """Adds a new job."""

    data = request.get_json(force=True)

    try:
        job = current_app.apscheduler.add_job(**data)
        return jsonify(job)
    except ConflictingIdError:
        logging.warning(f'Job {data.get("id")} already exists.')
        return jsonify(dict(error_message='Job %s already exists.' % data.get('id')), status=409)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


def delete_job(job_id):
    """Deletes a job."""

    try:
        current_app.apscheduler.remove_job(job_id)
        return Response(status=204)
    except JobLookupError:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


def get_job(job_id):
    """Gets a job."""

    job = current_app.apscheduler.get_job(job_id)

    if not job:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)

    return jsonify(job)


api_loader = TushareJsonApi()


def get_jobs():
    """Gets all scheduled jobs."""

    jobs = current_app.apscheduler.get_jobs()

    job_states = []

    for job in jobs:
        api = api_loader.get_api_by_name(job.name)
        reports = _report_container.get_reports(job.id, page_size=1)
        job_states.append({"job": job, "api": api, "reports": [r.to_dict() for r in reports]})

    return jsonify(job_states)


def update_job(job_id):
    """Updates a job."""

    data = request.get_json(force=True)

    try:
        current_app.apscheduler.modify_job(job_id, **data)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


def pause_job(job_id):
    """Pauses a job."""

    try:
        current_app.apscheduler.pause_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


def resume_job(job_id):
    """Resumes a job."""

    try:
        current_app.apscheduler.resume_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


def run_job(job_id):
    """Executes a job."""

    try:
        current_app.apscheduler.run_job(job_id)
        job = current_app.apscheduler.get_job(job_id)
        return jsonify(job)
    except JobLookupError:
        logging.warning(f'Job {job_id} not found.')
        return jsonify(dict(error_message='Job %s not found' % job_id), status=404)
    except Exception as e:
        logging.error(e, exc_info=True)
        return jsonify(dict(error_message=str(e)), status=500)


_report_container = ProcessReportContainer()


def get_job_results(job_id):
    status = request.args.get('status')
    page = request.args.get('page', default=0)
    page_size = request.args.get('size', default=20)
    results = _report_container.get_reports(job_id, status, page, page_size)
    if results:
        return jsonify([r.to_dict() for r in results])
    return jsonify([])
