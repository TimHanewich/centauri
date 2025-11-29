# Add parent directory to path so we can import utils.py (shared module)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

import utils

data = utils.pack_control_packet(1.0, 1.0, 1.0, 1.0)
print(str(data))