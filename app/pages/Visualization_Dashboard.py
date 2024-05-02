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

session_state = st.session_state

if 'data' not in st.session_state:
    st.session_state['data'] = 0


def update_data_state():
    st.session_state['data'] = 1


def filter_by_bioreplicate(df, bioreplicate_id):
    """
    Filter the DataFrame by Biological_Replicate_id
    
    Parameters:
        df (pandas.DataFrame): Input DataFrame
        bioreplicate_id (str): Biological_Replicate_id to filter by
    
    Returns:
        pandas.DataFrame: Filtered DataFrame containing rows with the specified Biological_Replicate_id,
                          or None if the Biological_Replicate_id is not found
    """
    filtered_df = df[df['Biological_Replicate_id'] == bioreplicate_id]
    if filtered_df.empty:
        return None
    return filtered_df



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

list_samples = []

if not df_growth.empty or not df_reads.empty:
    update_data_state()

checkbox_states = {}



with st.container():
    if st.session_state['data'] == 1:
        col1, col2 = st.columns([0.25, 0.75])
        with col1:
            df_experiments = getExperiments(studyID_to_visualize, conn)
            st.write("**Experiments**")
            for i, j, k in zip(df_experiments["experimentId"], df_experiments["experimentDescription"],  df_experiments["bioreplicateIds"]):
                with st.expander(f"{i}", expanded = True):
                    st.write(f"{j}")
                    biorep_list = k.split(",")
                    for rep in biorep_list:
                        key = f"checkbox_{i}_{rep}"
                        checkbox_state = checkbox_states.get(key, False)
                        checkbox_states[key] = st.checkbox(rep, checkbox_state)
                        if checkbox_states[key]:
                            list_samples.append(key)
        with col2:
            tab1, tab2, tab3 = st.tabs(["Growth", "Sequencing and FC counts", "Metabolites"])
            df_filtered_biorep = filter_by_bioreplicate(df_growth,)
            with tab1:

                if not list_samples:
                    st.warning("Select at least one biological replicate ID.")
                elif not df_growth.empty :
                    st.dataframe(df_growth)
                else:
                    st.warning("This study does not contain growth data.")
            with tab2:
                if not list_samples:
                    st.warning("Select at least one biological replicate ID.")
                elif not df_reads.empty:
                    st.dataframe(df_growth)
                else:
                    st.write("This study does contains sequencing or FC counts data.")



    else:
        st.write("chaiting")


print(list_samples)



            
