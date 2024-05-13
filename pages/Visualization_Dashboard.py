import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components
import sys
import os
filepath = os.path.realpath(__file__)
current_dir = os.path.dirname(filepath)
root_dir = os.path.dirname(current_dir)
relative_path_to_src = os.path.join(root_dir, 'src')
sys.path.append(relative_path_to_src)
from db_functions import getExperiments


# Configure page
st.set_page_config(page_title="Visualization Dashboard", layout='wide')
add_logo("figs/logo_sidebar3.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("Visualizing Study Data")
st.markdown("![badge](https://img.shields.io/badge/status-under%20development-orange?style=for-the-badge)")

conn = st.connection("BacterialGrowth", type="sql")

def dashboard():
    """
    If df_growth then init page with selected from Search page data
    else init the whole page.
    """

    import streamlit as st
    st.set_page_config(page_title="Visualization Dashboard", layout='wide')


    print("session state in dashboard:",st.session_state)


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
    from filter_df import filter_dict_states

    add_logo("figs/logo_sidebar2.png", height=100)
    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    df_growth = pd.DataFrame()
    df_reads = pd.DataFrame()

    # temporar
    if "to_dashboard" in st.session_state and st.session_state["to_dashboard"] != "":
        studyID_to_visualize = str(st.session_state["to_dashboard"])
    else:
        studyID_to_visualize = None

    if  "df_growth" not in st.session_state:
        st.session_state['df_growth'] = None

    if  "df_reads" not in st.session_state:
        st.session_state['df_reads'] = None

    data = None
    col1, col2 = st.columns([0.94, 0.06])

    if studyID_to_visualize is None:

        with col1:
            no_button = True
            studyID_to_visualize = st.text_input(
                label = "Study ID",
                placeholder="Enter the Study ID you want to visualize its data",
                help="Enter only numerical values"
                )
            if studyID_to_visualize != None:
                no_button = False


        with col2:
            st.write("")
            st.write("")
            go_button = st.button("Go!",type = "primary",disabled=no_button)


    if studyID_to_visualize != None or go_button:
        print(studyID_to_visualize)
        print(type(studyID_to_visualize))
        print("===================")
        path = relative_path_to_src + f"/Data/Growth/{studyID_to_visualize}"
        growth_file = path + f"/Growth_Metabolites.csv"
        reads_file = path + f"/Sequencing_Reads.csv"

        try:
            df_growth = pd.read_csv(growth_file)
            st.session_state['df_growth'] = 0
        except FileNotFoundError:
            df_growth = pd.DataFrame()

        try:
            df_reads = pd.read_csv(reads_file)
            st.session_state['df_reads'] = 0
        except FileNotFoundError:
            df_reads = pd.DataFrame()


    return df_growth, df_reads, studyID_to_visualize, conn

def content(df_growth, df_reads, studyID_to_visualize, conn):
    import streamlit as st
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
    from filter_df import filter_dict_states


    checkbox_states = {}

    #col1, col2, col3 = st.columns([0.25, 0.70, 0.5])
    #with col2:
    #    if not df_growth.empty :
    #        st.dataframe(df_growth)
    #    if not df_reads.empty:
    #        st.dataframe(df_growth)
    with col1:
        st.write("**Experiments**")

    if not df_growth.empty or not df_reads.empty:
        with col1:
            if not df_growth.empty:
                df_experiments = getExperiments(studyID_to_visualize, conn)
                for i, j, k in zip(df_experiments["experimentId"], df_experiments["experimentDescription"],  df_experiments["bioreplicateIds"]):
                    with st.expander(f"{i}"):
                        st.write(f"{j}")
                        biorep_list = k.split(",")
                        for rep in biorep_list:
                            checkbox_key = f"checkbox_{i}_{rep}"
                            checkbox_states[checkbox_key] = st.checkbox(f"{rep}", key=checkbox_key, value=checkbox_states.get(checkbox_key, False))
            else:
                st.warning("Study does not contain growth data")


        experiment_with_bioreps = filter_dict_states(st.session_state)
        return experiment_with_bioreps

def tabs_plots(experiment_with_bioreps):
    import streamlit as st
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
    from filter_df import filter_df

    with col2:
        result_growth_df_dict, result_reads_df_dict = filter_df(experiment_with_bioreps,df_growth,df_reads)
        print(result_growth_df_dict)
        print(result_reads_df_dict)
        tab1, tab2, tab3, tab4,tab5 = st.tabs(["OD", "Plate Counts","FC Counts","Reads 16S RNA","Metabolites"])
        with tab1:
            for exp, growth_df in result_growth_df_dict.items():
                st.write(f"OD in Experiment: {exp}")
                st.dataframe(growth_df)
                if 'OD' in growth_df.columns:
                    fig = px.line(growth_df, x='Time', y='OD',color='Biological_Replicate_id' ,title=f'OD Data for Experiment:{exp} per Biological replicates')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate ID selected do not contain OD data")
        with tab2:
            for exp, growth_df in result_growth_df_dict.items():
                st.write(f"Plate Counts: {exp}")
                st.dataframe(growth_df)
                if 'Plate_counts' in growth_df.columns:
                    fig = px.line(growth_df, x='Time', y='Plate_counts',color='Biological_Replicate_id' ,title=f'Plate Counts for Experiment:{exp} per Biological replicates')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("The Biological Replicate IDs selected do not contain Plate Counts data")










if __name__ == "__main__":
    import streamlit as st
    df_growth, df_reads, studyID_to_visualize, conn = dashboard()
    col1, col2, col3 = st.columns([0.25, 0.70, 0.5])
    experiment_with_bioreps=content(df_growth, df_reads, studyID_to_visualize, conn)
    print(experiment_with_bioreps)
    tabs_plots(experiment_with_bioreps)
    #content(df_growth, df_reads, studyID_to_visualize, conn)
