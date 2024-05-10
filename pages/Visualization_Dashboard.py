import streamlit as st
st.set_page_config(page_title="Visualization Dashboard", layout='wide')



import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components
import sys
import os

filepath = os.path.realpath(__file__)
current_dir = os.path.dirname(os.path.dirname(filepath))
relative_path_to_src = os.path.join(current_dir, 'src')
sys.path.append(relative_path_to_src)

from db_functions import getExperiments

add_logo("figs/logo_sidebar3.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

conn = st.connection("BacterialGrowth", type="sql")

st.title("Visualizing Study Data")


def dashboard():
    """
    If df_growth then init page with selected from Search page data
    else init the whole page.
    """

    df_growth = pd.DataFrame()
    df_reads = pd.DataFrame()

    # temporar
    if "to_dashboard" in st.session_state and st.session_state["to_dashboard"] != "":
        studyID_to_visualize = str(st.session_state["to_dashboard"])
    else:
        studyID_to_visualize = None

    with st.container():

        data = None
        col1, col2 = st.columns([0.94, 0.06])

        if studyID_to_visualize is None:

            with col1:
                studyID_to_visualize = st.text_input(
                    label = "Study ID",
                    placeholder="Enter the Study ID you want to visualize its data",
                    help="Enter only numerical values"
                )

            with col2:
                st.write("")
                st.write("")
                st.session_state.dontGo = studyID_to_visualize == ""
                go_button = st.button("Go!", disabled=st.session_state.dontGo, type = "primary")

            if studyID_to_visualize == None and go_button:
                st.warning("You need to provide a Study ID first!")

        else:
            go_button = True

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
        col1, col2, col3 = st.columns([0.25, 0.70, 0.5])
        if not df_growth.empty or not df_reads.empty:

            with col2:
                if not df_growth.empty :
                    st.dataframe(df_growth)
                if not df_reads.empty:
                    st.dataframe(df_growth)

            with col1:
                if not df_growth.empty:
                    df_experiments = getExperiments(studyID_to_visualize, conn)
                    st.write("**Experiments**")
                    for i, j, k in zip(df_experiments["experimentId"], df_experiments["experimentDescription"],  df_experiments["bioreplicateIds"]):
                        with st.expander(f"{i}"):
                            st.write(f"{j}")
                            biorep_list = k.split(",")
                            for rep in biorep_list:
                                st.checkbox(f"{rep}", key = f"checkbox_{i}_{rep}")
                            #st.write(df_growth["Biological_Replicate_id"])


if __name__ == "__main__":
    dashboard()
