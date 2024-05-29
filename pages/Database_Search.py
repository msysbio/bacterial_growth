import os
import sys
import streamlit as st
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components

st.set_page_config(page_title="Database Search", page_icon="🔍", layout='wide')

# Load local modules
current_dir = os.path.dirname(os.path.realpath(__file__))
repo_dir = os.path.dirname(os.path.dirname(current_dir))
relative_path_to_src = os.path.join(repo_dir, 'src')
sys.path.append(relative_path_to_src)
sys.path.append(current_dir)

from Visualization_Dashboard import dashboard
from db_functions import dynamical_query, getGeneralInfo, getExperiments, \
    getCompartment, getCommunities, getMicrobialStrains, getBiorep, getAbundance, \
    getFC, getMetabolite, getPerturbations
from edit_sessions import clean_dashboard


# Define the options for the dropdown list
options = ['Project Name', 'Project ID', 'Study Name', 'Study ID','Microbial Strain', 'NCBI ID','Metabolites', 'chEBI ID', 'pH']
options_logical = ['AND', 'OR', 'NOT']

# Define the range for the slider
min_value_ph = 0.0
max_value_ph = 14.0
min_value_ph_add = 0.0
max_value_ph_add = 14.0


def increase_rows():
    index = len(st.session_state['rows'])
    st.session_state['rows'][index + 1] = True


def decrease_rows(index):
    keys_to_remove = []
    for key in st.session_state:
        if key.endswith(str(index)):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del st.session_state[key]


def toggle_container(index):
    st.session_state['rows'][index] = not st.session_state['rows'][index]


def display_row(index):
    # """
    # Filters for advanced search
    # """
    advance_query = {}

    if index not in st.session_state['rows']:
        pass

    elif st.session_state['rows'][index]:

        with st.container():

            if f'add_query_clicked_{index}' not in st.session_state:
                st.session_state[f'add_query_clicked_{index}'] = False

            if f'delete_query_clicked_{index}' not in st.session_state:
                st.session_state[f'delete_query_clicked_{index}'] = False

            col1_add, col2_add, col3_add = st.columns([1, 1, 2])
            # Add a text input field to the first column
            with col1_add:
                logical_options = st.selectbox('Select logic opetator:', options_logical, key=f'box1_add{index}')
                advance_query['logic_operator'] = logical_options

            with col2_add:
                selected_option_add = st.selectbox('Select an option:', options,  key=f'box2_add{index}')
                advance_query['option'] = selected_option_add

            with col3_add:
                if selected_option_add == 'pH':
                    start_value_add, end_value_add = st.slider('Select a range:',
                                                               min_value_ph_add,
                                                               max_value_ph_add,
                                                               (min_value_ph_add, max_value_ph_add),
                                                               step=0.5,
                                                               key=f'slide1_add{index}',
                                                               format="%.1f"
                                                    )
                    advance_query['value'] = (start_value_add, end_value_add)
                else:
                    input_value_add = st.text_input('Enter Text here:', '', key=f'text1_add{index}')
                    advance_query['value'] = (input_value_add)


            if f'delete_query_visible_{index}' not in st.session_state:
                st.session_state[f'delete_query_visible_{index}'] = True

            if st.session_state[f'delete_query_visible_{index}']:
                if st.button('Delete',
                            key=f'delete_quern_{index}',
                            type='primary',
                            on_click=lambda: toggle_container(index)):
                    st.session_state[f'delete_query_visible_{index}'] = False
    return advance_query


def db_search():

    with open("style.css") as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
    st.image('figs/SearchBanner.png')


    st.session_state["IDEA"] = True


    st.markdown("![badge](https://img.shields.io/badge/status-under%20development-orange?style=for-the-badge)")
    st.markdown(
        """
        Discover microbial growth studies and datasets by selecting one or more of the options.
        When conducting an advanced search, you can choose multiple logical operators to refine your query and extract precise information from the database.

        To download the results of your search, simply select the checkboxes next to the studies you wish to download and then click on "Download Data".
        """
    )

    st.write('')
    st.write('')

    if 'rows' not in st.session_state:
        st.session_state['rows'] = {}
        st.session_state['rows'][1] = True

    all_advance_query = []
    first_query = {}

    # Use columns to lay out the elements side by side
    col1, col2 = st.columns([1, 2])

    # Add a text input field to the first column
    with col1:
        selected_option = st.selectbox('Select an option:', options, key='selectbox1')
        first_query['option'] = selected_option

    # Add a selectbox to the second column
    # input_value = None
    with col2:
        if selected_option == 'pH':
            start_value, end_value = st.slider('Select a range:', min_value_ph, max_value_ph, (min_value_ph, max_value_ph), step=0.5, key='range1', format="%.1f")
            first_query['value'] = (start_value, end_value)
        else:
            input_value = st.text_input('Enter Text here:', '', key='textinput1')
            first_query['value'] = input_value

    all_advance_query.append(first_query)


    # Function to render additional dropdown block
    advance_search = st.checkbox("Advanced Search", value=False)
    if advance_search:
        # Parse all novel strains (without a NCBI Taxonomy Id) added
        for i in range(1, len(st.session_state['rows']) + 1):
            st.write('')
            advance_query = display_row(i)
            all_advance_query.append(advance_query)

        st.button('Add More',
            key=f'add_query_{i}',
            type='primary',
            on_click=increase_rows
        )

    st.session_state.preventSearching = first_query["value"] == ""

    search_button = st.button(
        '**Search Data**',
        key='search_button',
        disabled=st.session_state.preventSearching,
        type='primary'
    )


    st.text("")
    st.text("")

    if "form" not in st.session_state:  # [NOTE]  Not sure why/if we need this..
        st.session_state.form = False

    # if search_button or st.session_state.form:
    if search_button or st.session_state.form:

        # Once search is clicked a table pops up
        # If a growth_df is clicked then jump into the dashboard page using that as input
        # thanks to the st.session_state


        final_query = dynamical_query(all_advance_query)

        conn = st.connection("BacterialGrowth", type="sql")
        df_studies = conn.query(final_query)  # , ttl=None

        num_results = len(df_studies)

        if num_results == 0:
            st.warning("Sorry, there is no studies in the database that match your search.")

        else:
            study_ids = []
            st.write(f'**{num_results}** search results')

            with st.form(key="Results"):

                #c1 , c2 = st.columns([0.05, 0.95])

                for i in range(len(df_studies)):

                    c1 , c2 = st.columns([0.05, 0.95])
                    with c1:
                        down_check = st.checkbox(f"{i+1}",key=f'checkbox{i}')

                    with c2:
                        study_id = df_studies['studyId'][i]
                        study_ids.append(study_id)
                        df_general = getGeneralInfo(study_id, conn)
                        print(df_general)
                        study_name = df_general['studyName'][0]
                        transposed_df = df_general.T
                        studyname = st.page_link("pages/Visualization_Dashboard.py",
                                                label= f':blue[**{study_name}**]'
                                    )

                        formatted_html = transposed_df.to_html(render_links=True, escape=False, justify='justify', header = False)
                        styled_html = f"<style>table {{ font-size: 13px; }}</style>{formatted_html}"
                        table = st.markdown(styled_html, unsafe_allow_html=True)

                        space = st.text("")

                        with st.expander("**Experiments**"):
                            df_experiments = getExperiments(study_id, conn)
                            st.dataframe(df_experiments,hide_index=True,)

                        space = st.text("")

                        with st.expander("**Compartments**"):
                            df_Compartment = getCompartment(study_id, conn)
                            st.dataframe(df_Compartment,hide_index=True,)

                        space = st.text("")

                        with st.expander("**Microbial Strains and Communities**"):
                            df_Community = getCommunities(study_id, conn)
                            if not df_Community.empty:
                                st.write("**Communities information**")
                                st.dataframe(df_Compartment,hide_index=True,)
                            df_strains = getMicrobialStrains(study_id, conn)
                            if not df_strains.empty:
                                st.write("**Community Members information**")
                                st.dataframe(df_strains,hide_index=True,)

                        space = st.text("")

                        with st.expander("**Biological Replicates, Growth and Metabolites Measurements**"):
                            df_biorep = getBiorep(study_id, conn)
                            if not df_biorep.empty:
                                st.write("**Biological Replicates Metadata**")
                                st.dataframe(df_biorep,hide_index=True,)
                            
                            df_abundance = getAbundance(study_id, conn)
                            if not df_abundance.empty:
                                st.write("**Abundance data per Biological Replicates and microbial species**")
                                st.dataframe(df_abundance,hide_index=True,)

                            df_FC = getFC(study_id, conn)
                            if not df_FC.empty:
                                st.write("**Flow Cytometry Counts data per Biological Replicates and microbial species**")
                                st.dataframe(df_FC,hide_index=True,)

                            df_Metabolite = getMetabolite(study_id, conn)
                            if not df_Metabolite.empty:
                                st.write("**Metabolites measured per Biological Replicates**")
                                st.dataframe(df_Metabolite,hide_index=True,)

                        space = st.text("")
                        df_perturbation = getPerturbations(study_id, conn)
                        if not df_perturbation.empty:
                            with st.expander("**Perturbations**"):
                                    st.dataframe(df_perturbation,hide_index=True,)


                print("Checkboxes:", down_check)

                space2 = st.text("")
                download = st.form_submit_button("Dowload Data", type = 'primary')
                if download:
                    st.write('bla')


            # Out of the form
            if not df_general.empty:
                st.session_state.to_dashboard = study_ids[-1]

                st.page_link("pages/Visualization_Dashboard.py", label="View selected on Dashboard")



    # conn = st.connection("BacterialGrowth", type="sql")

    # # Perform query.
    # df_study = conn.query('SELECT * from Study;', ttl=600)
    # st.dataframe(df_study)

    # df_biologicalrep = conn.query('SELECT * from Experiments;', ttl=600)
    # st.dataframe(df_biologicalrep)

    # df_technicalrep = conn.query('SELECT * from Compartments;', ttl=600)
    # st.dataframe(df_technicalrep)

    # df_ReactorSetUp = conn.query('SELECT * from Strains;', ttl=600)
    # st.dataframe(df_ReactorSetUp)

    # df_Compartments = conn.query('SELECT * from Community;', ttl=600)
    # st.dataframe(df_Compartments)

    # df_Bacteria = conn.query('SELECT * from CompartmentsPerExperiment;', ttl=600)
    # st.dataframe(df_Bacteria)

    # df_metabolites = conn.query('SELECT * from TechniquesPerExperiment;', ttl=600)
    # st.dataframe(df_metabolites)

    # df_metabolitesyn = conn.query('SELECT * from BioReplicatesPerExperiment;', ttl=600)
    # st.dataframe(df_metabolitesyn)

    # df_metabolite_repl = conn.query('SELECT * from Perturbation;', ttl=600)
    # st.dataframe(df_metabolite_repl)

    # df_metabolitedb = conn.query('SELECT * from Metabolites;', ttl=600)
    # st.dataframe(df_metabolitedb)

    # df_Abundances = conn.query('SELECT * from Abundances;', ttl=600)
    # st.dataframe(df_Abundances)

    # df_FC_couts = conn.query('SELECT * from FC_Counts;', ttl=600)
    # st.dataframe(df_FC_couts)

    # df_BioReplicatesMetadata = conn.query('SELECT * from BioReplicatesMetadata', ttl=600)
    # st.dataframe(df_BioReplicatesMetadata)

    # df_MetabolitePerReplicates = conn.query('SELECT * from MetabolitePerExperiment;', ttl=600)
    # st.dataframe(df_MetabolitePerReplicates)




if 'IDEA' in st.session_state:
    print("MONO MIA FORA RE MALAKA TAKI")


else:
    print("TAKI TON IPIES - PALI MIDEN")
    try:
        print("TAKI KATHARISE")
        clean_dashboard()
    except:
        print("POS GINETAI NA MI MPOREIS NA KATHARISEIS RE MALAKA TAKI")
        pass
    button_enabled = False

# Confing st page
# st.set_page_config(page_title="Database Search", page_icon="🔍", layout='wide')
add_logo("figs/logo_sidebar3.png", height=100)

db_search()