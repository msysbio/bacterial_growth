import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))[:-3]
relative_path_to_src = os.path.join(current_dir, 'src')
sys.path.append(relative_path_to_src)
from constants import *


