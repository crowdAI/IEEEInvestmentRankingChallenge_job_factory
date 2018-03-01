#!/usr/bin/env python
import pandas as pd
import numpy as np


def check_file_validity(data, ground_truth):
    """
    Check whether the target and test file are compatible.
    The dataframes columns, sensor ids and timestamps are checked.

    :param data: target data
    :param ground_truth: real data
    :return: validity
    """
    valid = True
    valid &= len(data) == len(ground_truth)
    valid &= np.all(data.columns == ground_truth.columns)
    if valid:
        valid &= np.all(data.sensor == ground_truth.sensor)
        valid &= np.all(data.ts == ground_truth.ts)

    if not valid:
        raise Exception("The submitted file does not seem to be a valid submission file.")
        # TODO: You can add more checks and better error messages here

    return valid


def compute_mape(data, ground_truth):
    """
    Compute the mean absolute percentage error

    With a_i being the actual values and f_i the forecast value:
    mape = 100 / n * sum_{i=1}^n |(a_i - f_i) / a_i)|

    :param data: target data to test
    :param ground_truth: real values
    :return: MAPE
    """
    return 100 / len(ground_truth) * np.sum(np.abs((ground_truth.value - data.value) / ground_truth.value))


def _evaluate(client_payload, answer_file_path, context):
    """
        client_payload : Object holding the client payload
            -predicted_data_path: Path to the submitted file
        answer_file_path : Path to the gold label
        context: Extra params for Advanced usage
    """

    """
    Load submission data and gold labels
    """
    predicted_data_path = client_payload['predicted_data_path']
    predicted_data = pd.read_csv(predicted_data_path, float_precision='round_trip')

    ground_truth = pd.read_csv(answer_file_path, float_precision='round_trip')
    # Format validation
    check_file_validity(predicted_data, ground_truth)
    # Score calculation
    score = compute_mape(predicted_data, ground_truth)

    _result_object = {
        "score": score,
        "score_secondary": 0,
    }

    return _result_object


if __name__ == "__main__":
    client_payload = {}
    client_payload["predicted_data_path"] = "temp/sample_submission.csv"

    _answer_file_path = "data/ground_truth.csv"

    _context = {}
    print(
        _evaluate(
            client_payload,
            _answer_file_path,
            _context)
        )
