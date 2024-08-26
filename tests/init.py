import os
import sys

# Make sure that database connections created in the code connect to the test
# database:
os.environ['APP_ENV'] = 'test'

# Inside of "src" modules import other packages in "src":
sys.path.append('src')
