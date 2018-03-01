# Kit Energy Challenge Job Factory


## Installation (For crowdAI admins)
```
git clone git@github.com:crowdAI/crowdAI-KIT-energy-challenge-job-factory.git
cd crowdAI-KIT-energy-challenge-job-factory
pip install -r requirements.txt
```

## Usage (For crowdAI admins)
```
cp config.py.example config.py
# Edit config.py to add your relevant
python run.py #Runs the interface of interacting with the broker
rqworker -c settings # Runs the actual worker(s)
```

## Usage for Challenge Oragnisers
```
git clone git@github.com:crowdAI/crowdAI-KIT-energy-challenge-job-factory.git
cd crowdAI-KIT-energy-challenge-job-factory
pip install -r requirements.txt
```

Then you need to define a class for your challenge similar to `kit_energy_evaluator.py`
The simplest definition can be :
```
import pandas as pd
class ExampleEvaluator:
  def __init__(self, answer_file_path):
    self.answer_file_path = answer_file_path

  def _evaluate(self, submission_file_path):
    submission = pd.read_csv("submission_file_path")

    """
    Do something with your submitted file to come up
    with a score and a secondary score.

    if you want to report back an error to the user,
    then you can simply do :
      `raise Exception("YOUR-CUSTOM-ERROR")`
    """
    _result_object = {
        "score": np.random.random(),
        "score_secondary" : np.random.random()
    }
    return _result_object
```

## Installation (for participants)
```
pip install --upgrade crowdai
# This challenge expects atleast crowdai client version 1.0.15
```

## Usage (for participants)

```
import crowdai
api_key = "YOUR CROWDAI API KEY HERE"
challenge = crowdai.Challenge("KITEnergyChallenge", api_key)
result = challenge.submit("sample_submission.csv")
print(result)
```

# Author
S.P. Mohanty <sharada.mohanty@epfl.ch>    
