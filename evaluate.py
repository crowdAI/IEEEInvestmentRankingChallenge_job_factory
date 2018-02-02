#!/usr/bin/env python
import pandas as pd
from sklearn.metrics import f1_score

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
    predicted_data = pd.read_csv(predicted_data_path)

    answer_file = pd.read_csv(answer_file_path)

    """
    IMPORTANT : Also do your custom validation
    #TODO
    """
    assert(len(predicted_data) == len(answer_file))

    predictions = predicted_data["predicted_class_idx"].tolist()
    answer = answer_file["correct_class_idx"].tolist()

    score = f1_score(answer, predictions, average="weighted")

    """
    Validation done here
    """
    # raise("Example Error Message")

    _result_object = {
        "score" : score,
        "score_secondary" : 0,
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
