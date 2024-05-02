import streamlit as st
st.set_page_config(page_title="Visualization Dashboard", layout='wide')

import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components
import sys
import os




current_dir = os.path.dirname(os.path.realpath(__file__))[:-9]
relative_path_to_src = os.path.join(current_dir, 'src')

sys.path.append(relative_path_to_src)
from db_functions import getExperiments


add_logo("figs/logo_sidebar2.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

df_growth = pd.DataFrame()
df_reads = pd.DataFrame()
conn = st.connection("BacterialGrowth", type="sql")

st.title("Visualizing Study Data")

with st.container():
    data = None
    studyID_to_visualize = None
    col1, col2 = st.columns([0.94, 0.06])
    with col1:
        studyID_to_visualize = st.text_input(label = "Study ID",placeholder="Enter the Study ID you want to visualize its data", help="Enter only numerical values")
    with col2:
        st.write("")
        st.write("")
        no_button = True
        go_button = st.button("Go!",type = "primary")

    if studyID_to_visualize == None and go_button:
        st.warning("You need to provide a Study ID first!")
    if studyID_to_visualize != None and go_button:
        path = relative_path_to_src + f"/Data/Growth/{studyID_to_visualize}"
        growth_file = path + f"/Growth_Metabolites.csv"
        reads_file = path + f"/Sequencing_Reads.csv"


        try:
            df_growth = pd.read_csv(growth_file)
        except FileNotFoundError:
            df_growth = pd.DataFrame()

        try:
            df_reads = pd.read_csv(reads_file)
        except FileNotFoundError:
            df_reads = pd.DataFrame()

        if df_growth.empty or df_reads.empty:
            st.warning("This Study ID is invalid, check and try again with a correct ID.")


with st.container():
    col1, col2, col3 = st.columns([0.20, 0.75 ,0.5])
    if not df_growth.empty or not df_reads.empty:
        with col2:
            if not df_growth.empty :
                st.dataframe(df_growth)
            if not df_reads.empty:
                st.dataframe(df_growth)
        with col1:
            if not df_growth.empty:
                #st.write("bla")
                df_experiments = getExperiments(studyID_to_visualize, conn)
                st.write("**Experiments**")
                for i in df_experiments["experimentId"]:
                    with st.expander(f"{i}"):
                        for j in set(df_growth["Biological_Replicate_id"]):
                            st.checkbox(f"{j}", key = f"checkbox_{i}_{j}")
                        #st.write(df_growth["Biological_Replicate_id"])
            
