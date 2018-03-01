from config import Config as config
import redis
from rq import get_current_job
import os

from helpers import _update_job_event, download_file, report_to_crowdai
from utils import job_info_template, job_complete_template
from utils import job_error_template, job_running_template

if config.redis_password:
    POOL = redis.ConnectionPool(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password)
else:
    POOL = redis.ConnectionPool(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db)


def _submit(client_payload, answer_file_path, context):
    """
        takes a list of predicted heights and actual heights
        and computes the score
        and prepares the plots for submission to the leaderboard
    """
    file_key = client_payload["file_key"]
    _update_job_event(
        context,
        job_info_template(
            context, "Grading Submission....")
    )

    _payload = {}
    _meta = {}
    _meta['file_key'] = file_key
    _payload["meta"] = _meta
    submission_id = report_to_crowdai(
                    context,
                    _payload,
                    submission_id=False,
                    status='submitted')
    try:
        localfilepath = download_file(context, file_key)
        _client_payload = {}
        _client_payload["predicted_data_path"] = localfilepath

        _result_object = config.evaluator._evaluate(
            _client_payload,
            context)

        _payload = _result_object
        report_to_crowdai(
                        context,
                        _payload,
                        submission_id=submission_id,
                        status='graded')
        # Clean up file if possible
        os.remove(localfilepath)
        return _result_object
    except Exception as e:
        # Report to crowdAI
        if "meta" in _payload.keys():
            del _payload["meta"]
        report_to_crowdai(
                        context,
                        _payload,
                        submission_id=submission_id,
                        status='failed',
                        message=str(e)
                        )
        # raise the exception again
        # so that it can be handled further down the chain
        raise e

def job_execution_wrapper(data):
    redis_conn = redis.Redis(connection_pool=POOL)
    job = get_current_job()

    _context = {}
    _context['redis_conn'] = redis_conn
    _context['response_channel'] = data['broker_response_channel']
    _context['job_id'] = job.id
    _context['data_sequence_no'] = data['data_sequence_no']
    _context['api_key'] = data['extra_params']['api_key']

    # Register Job Running event
    _update_job_event(
        _context,
        job_running_template(_context['data_sequence_no'], job.id)
        )
    result = {}
    try:
        if data["function_name"] == "grade_submission":
            # Run the job
            answer_file_path = config.answer_file_path

            result = _submit(data["data"], answer_file_path, _context)
            # Register Job Complete event
            _update_job_event(
                _context,
                job_info_template(
                    _context, "Scores Submitted Successfully ! Mean Absolute Percentage Error (MAPE) : %s" % (str(result['score'])))
                )
            _update_job_event(
                _context,
                job_complete_template(_context, result)
                )
        else:
            _error_object = job_error_template(
                job.id,
                "Function not implemented error"
                )
            _update_job_event(
                _context,
                job_error_template(job.id, result)
                )
            result = _error_object
    except Exception as e:
        _error_object = job_error_template(
            _context['data_sequence_no'],
            job.id,
            str(e)
            )
        _update_job_event(_context, _error_object)
    return result
