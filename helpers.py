#!/usr/bin/env python

import uuid
import requests
import json
import os
import boto3
from config import Config as config

def _update_job_event(_context, data):
    """
        Helper function to serialize JSON
        and make sure redis doesnt messup JSON validation
    """
    redis_conn = _context['redis_conn']
    response_channel = _context['response_channel']
    data['data_sequence_no'] = _context['data_sequence_no']
    redis_conn.rpush(response_channel, json.dumps(data))


def report_to_crowdai(_context, _payload, submission_id=False,
                      status=False, message=""):
    print(_context, _payload, submission_id, status, message)
    if config.DEBUG_MODE:
        return str(uuid.uuid4())

    headers = {
        'Authorization': 'Token token='+config.CROWDAI_TOKEN,
        "Content-Type": "application/vnd.api+json"
        }
    _payload['challenge_client_name'] = config.challenge_id
    _payload['api_key'] = _context['api_key']
    if len(message) > 0:
        _payload['grading_message'] = message
    if status:
        _payload['grading_status'] = status
    print("Payload : ", _payload)
    if not submission_id:
        print "Making POST request...."
        r = requests.post(
            config.CROWDAI_GRADER_URL,
            params=_payload, headers=headers, verify=False)
    else:
        print "Making PATCH request...."
        r = requests.patch(
            "{}/{}".format(config.CROWDAI_GRADER_URL, submission_id),
            params=_payload, headers=headers, verify=False
        )

    print("RESPONSE : ", r.text)
    if r.status_code == 202:
        data = json.loads(r.text)
        submission_id = str(data['submission_id'])
        return submission_id
    else:
        _message = """
            Unable to register submission on crowdAI.
            Please contact the admins."""
        response = json.loads(r.text)
        _message = response['message']
        raise Exception(_message)


def get_boto_client():
    return boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )


def download_file(_context, filekey):
    # Download MIDI to tempfolder
    s3 = get_boto_client()
    filepath = "{}/{}".format(
        config.TEMP_STORAGE_DIRECTORY_PATH,
        str(uuid.uuid4())+".csv"
        )
    s3.download_file(
                    config.AWS_S3_BUCKET,
                    filekey,
                    filepath
                    )
    return filepath
