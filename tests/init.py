import os

# Make sure that database connections created in the code connect to the test
# database:
os.environ['APP_ENV'] = 'test'
