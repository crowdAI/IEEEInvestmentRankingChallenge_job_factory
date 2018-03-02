#!/usr/bin/env python
import pandas as pd
import numpy as np


class KITEnergyEvaluatror:
    def __init__(self, answer_file_path):
        """
        Initialise an evaluator

        :param answer_file_path : Path to the gold label
        """
        self.answer_file_path = answer_file_path
        self.ground_truth = pd.read_csv(
                            answer_file_path,
                            float_precision='round_trip'
                            )

    def check_file_validity(self, data):
        if len(data) != len(self.ground_truth):
            raise Exception("Expected '{}' rows but the submitted file has '{}'.".format(len(self.ground_truth),
                                                                                         len(data)))
        if np.any(data.columns != self.ground_truth.columns):
            raise Exception("Expected columns '{}' but the submitted file has '{}'.".format(
                str(self.ground_truth.columns.values),
                str(data.columns.values)))
        if np.any(data.ts != self.ground_truth.ts):
            raise Exception("The row order in the submitted file is incorrect (incorrect timestamp order).")
        if np.any(data.sensor != self.ground_truth.sensor):
            raise Exception("The row order in the submitted file is incorrect (incorrect sensor id order).")
        return True

    def compute_mape(self, data):
        """
        Compute the mean absolute percentage error

        With a_i being the actual values and f_i the forecast value:
        mape = 100 / n * sum_{i=1}^n |(a_i - f_i) / a_i)|

        :param data: target data to test
        :return: MAPE
        """
        return float(100) / len(self.ground_truth) * np.sum(np.abs((self.ground_truth.value - data.value) / self.ground_truth.value))

    def _evaluate(self, client_payload, context={}):
        """
            :param client_payload : Object holding the client payload
                -predicted_data_path: Path to the submitted file
            :param context : Object holding extra parameters for advanced usage
        """

        """
        Load submission data and gold labels
        """
        predicted_data_path = client_payload['predicted_data_path']
        predicted_data = pd.read_csv(predicted_data_path, float_precision='round_trip')

        # Format validation
        self.check_file_validity(predicted_data)
        # Score calculation
        score = self.compute_mape(predicted_data)

        _result_object = {
            "score": score,
            "score_secondary": 0,
        }

        return _result_object


if __name__ == "__main__":
    client_payload = {}
    client_payload["predicted_data_path"] = "temp/sample_submission.csv"
    _answer_file_path = "data/ground_truth.csv"

    evaluator = KITEnergyEvaluatror(_answer_file_path)
    _context = {}
    result = evaluator._evaluate(client_payload)
    print(result)
