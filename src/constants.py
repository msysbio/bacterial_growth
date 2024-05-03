import re
import os
# global PROJECT_DIRECTORY
# global LOCAL_DIRECTORY
# global BIOLOGICAL_REPLICATE_ANALYSIS_FILE
# global MEDIA_ANALYSIS_FILE
# global HEADERS_FILE
# global BIOLOGICAL_REPLICATES_LIST
# global MEDIA_LIST
global od_regex
global counts_regex
global qpcr_regex
global rnaseq_regex
global abundance_options

# This directory MUST BE the one where the core is in the server
current_file_path = os.path.abspath(__file__)
parent_folder = os.path.dirname(current_file_path)
root_folder = os.path.dirname(parent_folder)

# This directory MUST BE the one where the core is in the server
PROJECT_DIRECTORY = os.path.join(root_folder, "")
LOCAL_DIRECTORY = os.path.join(root_folder, "")
LOCAL_DIRECTORY_APP = os.path.join(LOCAL_DIRECTORY, "app")
LOCAL_DIRECTORY_TEMPLATES = os.path.join(LOCAL_DIRECTORY_APP, "templates")
LOCAL_DIRECTORY_YAML = os.path.join(LOCAL_DIRECTORY_TEMPLATES, "yaml_templates")


# Bash files needed to run the code
BIOLOGICAL_REPLICATE_ANALYSIS_FILE = 'src/bash_scripts/lab_files_analysis.sh'
MEDIA_ANALYSIS_FILE = 'src/bash_scripts/media_file_analysis.sh'
BIOLOGICAL_REPLICATES_LIST = 'IntermediateFiles/listOfFiles.list'
MEDIA_LIST = 'IntermediateFiles/listOfMedia.list'

# Database credentials
secrets_file = os.path.join(root_folder, "app/.streamlit/secrets.toml")
secrets = [line.strip() for line in open(secrets_file, 'r').readlines() if line.strip()]
secrets_dict = dict(line.split(' = ', 1) for line in secrets[1:])

USER = secrets_dict["username"].replace('"', '')
PASSWORD = secrets_dict["password"].replace('"', '')
HOST = secrets_dict["host"].replace('"', '')
PORT = secrets_dict["port"].replace('"', '')
DATABASE = secrets_dict["database"].replace('"', '')




# File types
file_types = ['abundanceFile', 'metabolitesFile', 'phFile']

# Abundance options
abundance_options = ['od', 'counts', 'qpcr', 'rnaseq']
# Regex options
abundance_regex = re.compile(r'.*time.* | .*liquid.* | .*active.* | .*OD.*', flags=re.I | re.X)
# abundance_regex = re.compile(r'time | liquid | active | OD', flags=re.I | re.X)
ph_regex = re.compile(r'.*time.* | .*ph.*', flags=re.I | re.X)
od_regex = re.compile(r'.*time.* | .*OD.*', flags=re.I | re.X)
counts_regex = re.compile(r'.*time.* | .*count.*', flags=re.I | re.X)
qpcr_regex = re.compile(r'.*time.* | .*qpcr.*', flags=re.I | re.X)
rnaseq_regex = re.compile(r'.*time.* | .*rna.*', flags=re.I | re.X)
biol_rep_metadata_fields = ['plateId', 'platePosition', 'initialPh', 'initialTemperature', 'inoculumConcentration', 'inoculumVolume', 'carbonSource', 'antibiotic']
pert_metadata_fields = ['property', 'newValue', 'startTime', 'endTime']