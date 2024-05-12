import streamlit as st
import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))[:-9]
relative_path_to_src = os.path.join(current_dir, 'src')
sys.path.append(relative_path_to_src)
from constants import *

conn = st.connection("BacterialGrowth", type="sql")


def getStudyID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Study;"
    number_projects = conn.query(query, ttl=600)
    next_number = int(number_projects.iloc[0].iloc[0]) + 1
    Study_ID = "SMGDB{:08d}".format(next_number)
    print(Study_ID)
    return Study_ID

Study_ID = getStudyID(conn)
print(Study_ID)
print(type(Study_ID))

print(os.path.join(LOCAL_DIRECTORY_YAML, 'STUDY.yaml'))