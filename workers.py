from config import Config as config
from job_states import JobStates
from utils import *

import redis
from rq import get_current_job
import time
import json

import sys
import random

from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

import requests

from evalute import _evaluate

POOL = redis.ConnectionPool(host=config.redis_host, port=config.redis_port, db=0)

def _submit(predicted_data_path, answer_file_path, context):
    """
        takes a list of predicted heights and actual heights and computes the score

        and prepares the plots for submission to the leaderboard
    """
    _result_object = _evaluate(predicted_data_path, answer_file_path, context)


    # Upload result to crowdai
    headers = {'Authorization' : 'Token token='+config.CROWDAI_TOKEN, "Content-Type":"application/vnd.api+json"}

    _payload = _result_object
    _payload['challenge_client_name'] = config.challenge_id
    _payload['api_key'] = context['api_key']
    _payload['grading_status'] = 'graded'
    _payload['comment'] = "" #TODO: Allow participants to add comments to submissions

    print "Making POST request...."
    r = requests.post(config.CROWDAI_GRADER_URL, params=_payload, headers=headers, verify=False)
    print "Status Code : ",r.status_code

    if r.status_code == 202:
        data = json.loads(r.text)
        submission_id = str(data['submission_id'])
        _payload['data'] = predicted_data_path
        context['redis_conn'].set(config.challenge_id+"::submissions::"+submission_id, json.dumps(_payload))
        pass #TODO: Add success message
    else:
        raise Exception(str(r.text))
    return _result_object

def _update_job_event(_context, data):
    """
        Helper function to serialize JSON
        and make sure redis doesnt messup JSON validation
    """
    redis_conn = _context['redis_conn']
    response_channel = _context['response_channel']
    data['data_sequence_no'] = _context['data_sequence_no']

    redis_conn.rpush(response_channel, json.dumps(data))

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
    _update_job_event(_context, job_running_template(_context['data_sequence_no'], job.id))
    result = {}
    try:
        if data["function_name"] == "submit":
            # Run the job
            answer_file_path = config.answer_file_path

            result = _submit(data["data"], answer_file_path, _context)
            # Register Job Complete event
            _update_job_event(_context, job_info_template(_context, "Scores Submitted Successfully ! Coefficient of Determination(R^2) : %s ; MSE : %s" % (str(result['score']), str(result['score_secondary'])) ))
            _update_job_event(_context, job_complete_template(_context, result))
        else:
            _error_object = job_error_template(job.id, "Function not implemented error")
            _update_job_event(_context, job_error_template(job.id, result))
            result = _error_object
    except Exception as e:
        _error_object = job_error_template(_context['data_sequence_no'], job.id, str(e))
        _update_job_event(_context, _error_object)
    return result
