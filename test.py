#!/usr/bin/env python
import unittest
from copy import copy
from tempfile import NamedTemporaryFile

import pandas as pd

from evaluate import _evaluate


class TestKitEnergyEvaluator(unittest.TestCase):
    """
    Unit tests for mape evaluator
    """
    GROUND_TRUTH = pd.DataFrame({
        'sensor': [1, 1, 1, 1, 1],
        'ts': [pd.Timestamp('2018-01-01T00:00:00.000+01:00'),
               pd.Timestamp('2018-01-01T00:00:15.000+01:00'),
               pd.Timestamp('2018-01-01T00:00:30.000+01:00'),
               pd.Timestamp('2018-01-01T00:45:00.000+01:00'),
               pd.Timestamp('2018-01-01T01:00:00.000+01:00')],
        'value': [0.5, 0.6, 0.7, 0.8, 0.9]
    })

    def test_wrong_columns(self):
        """
        Test with wrong column names in the prediction file
        :return: Should fail
        """
        prediction = copy(self.GROUND_TRUTH)
        prediction.columns = ['sensor', 'ts', 'foo']
        try:
            self.run_scenario(prediction)
        except AssertionError:
            return
        raise AssertionError('should raise an exception')

    def test_wrong_length(self):
        """
        Test with wrong length of the prediction file
        :return: Should fail
        """
        prediction = copy(self.GROUND_TRUTH)
        prediction = prediction.drop(0)
        try:
            self.run_scenario(prediction)
        except AssertionError:
            return
        raise AssertionError('should raise an exception')

    def test_wrong_order(self):
        """
        Test with the wrong row order in the prediction file
        :return: Should fail
        """
        prediction = copy(self.GROUND_TRUTH)
        prediction = prediction.sort_values('value', ascending=False)
        try:
            self.run_scenario(prediction)
        except AssertionError:
            return
        raise AssertionError('should raise an exception')

    def test_correct_submission(self):
        """
        Test with a correctly formatted prediction file
        :return: Should submit
        """
        prediction = copy(self.GROUND_TRUTH)
        prediction.value = [1.0, .6, .7, .8, .9]
        result = self.run_scenario(prediction)
        self.assertEqual(type(result), dict)
        self.assertSetEqual(set(result.keys()), {'score', 'score_secondary'})
        self.assertAlmostEqual(result['score'], 20.)

    def test_perfect_submission(self):
        """
        Test with a perfect submission
        :return: Should submit
        """
        prediction = copy(self.GROUND_TRUTH)
        result = self.run_scenario(prediction)
        self.assertEqual(type(result), dict)
        self.assertSetEqual(set(result.keys()), {'score', 'score_secondary'})
        self.assertAlmostEqual(result['score'], .0)

    def run_scenario(self, prediction):
        """
        Run a test scenario
        :param prediction: target submission
        :return: result of the evaluation
        """
        prediction_tmp_file = NamedTemporaryFile()
        prediction.to_csv(prediction_tmp_file.name, index=False)
        ground_truth_tmp_file = NamedTemporaryFile()
        self.GROUND_TRUTH.to_csv(ground_truth_tmp_file.name, index=False)
        client_payload = {'predicted_data_path': prediction_tmp_file.name}
        result = _evaluate(client_payload, ground_truth_tmp_file.name, {})
        prediction_tmp_file.close()
        ground_truth_tmp_file.close()
        return result


if __name__ == '__main__':
    unittest.main()
