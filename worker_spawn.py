import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rq.cli import worker
if __name__ == '__main__':
    sys.exit(worker())
