# OpenSNPChallenge2017_job_factory

Implementation of a CrowdAI Job Factory for the CrowdAI OpenSNPChallenge2017

# Installation Instructions
```
sudo apt-get install redis-server
git clone git@github.com:spMohanty/OpenSNPChallenge2017_job_factory.git
cd OpenSNPChallenge2017_job_factory
pip install -r requirements.txt
python run.py
# Then in a separate tab
rqworker
# Then in a separate tab
rq-dashboard
```

# Author
S.P. Mohanty <sharada.mohanty@epfl.ch>
