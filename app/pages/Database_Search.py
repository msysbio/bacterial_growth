import streamlit as st
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components
#from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

st.set_page_config(page_title="Database Search", page_icon="🔍", layout='wide')

add_logo("figs/logo_sidebar2.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


# Add a title to your Streamlit app
st.image('figs/SearchBanner.png')
#st.title('Search Studies and Experiments!')

st.markdown(
    """
    Discover studies and datasets by selecting one or more of the optional parameters: Study Name, Organism, Metabolite, chEBI ID, and pH.
    When conducting an advanced search, you can choose multiple logical operators to refine your query and extract precise information from the database.

    To download the results of your search, simply select the checkboxes next to the studies you wish to download and then click on "Download Data".
""")

st.write('')
st.write('')

# Define the options for the dropdown list
options = ['Project Name', 'Project ID', 'Study Name', 'Study ID','Microbial Strain', 'NCBI ID','Metabolites', 'chEBI ID', 'pH']
options_logical = ['AND', 'OR', 'NOT']

# Define the range for the slider
min_value_ph = 0.0
max_value_ph = 14.0
min_value_ph_add = 0.0
max_value_ph_add = 14.0

if 'rows' not in st.session_state:
    st.session_state['rows'] = {}
    st.session_state['rows'][1] = True

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
                    start_value_add, end_value_add = st.slider('Select a range:', min_value_ph_add, max_value_ph_add, (min_value_ph_add, max_value_ph_add), step=0.5, key=f'slide1_add{index}', format="%.1f")
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


all_advance_query = []
first_query = {}
# Use columns to lay out the elements side by side
col1, col2 = st.columns([1, 2])

# Add a text input field to the first column
with col1:
    selected_option = st.selectbox('Select an option:', options, key='selectbox1')
    first_query['option'] = selected_option

    # Add a selectbox to the second column
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
if advance_search == True:
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


search_button = st.button('**Search Data**',type='primary')

st.text("")
st.text("")

if "form" not in st.session_state:
    st.session_state.form = False

def getGeneralInfo(studyID, conn):
    query = f"SELECT * FROM Study WHERE studyId = {studyID};"
    df_general = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId','projectUniqueID','studyUniqueID']
    df_general.drop(columns_to_exclude, axis=1)
    query = f"SELECT CONCAT(memberName, ' (', NCBId, ')') AS transformed_output FROM Strains WHERE studyId = {studyID};"
    micro_strains = conn.query(query, ttl=600)
    df_general['memberName'] = ', '.join(micro_strains['transformed_output'])
    query = f"SELECT DISTINCT technique FROM TechniquesPerExperiment WHERE studyId = {studyID};"
    techniques = conn.query(query, ttl=600)
    df_general['techniques'] = ', '.join(techniques['technique'])
    query = f"SELECT DISTINCT CONCAT(metabo_name, ' (', cheb_id, ')') AS transformed_output FROM MetabolitePerExperiment WHERE studyId = {studyID};"
    metabolites = conn.query(query, ttl=600)
    df_general['metabolites'] = ', '.join(metabolites['transformed_output'])

    return df_general.drop(columns=columns_to_exclude)



def getExperiments(studyID, conn):
    query = f"""
    SELECT 
        E.experimentUniqueId,
        E.experimentId,
        E.experimentDescription,
        E.cultivationMode,
        GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds,
        E.controlDescription,
        GROUP_CONCAT(DISTINCT BR.bioreplicateId) AS control_bioreplicateIds,
        GROUP_CONCAT(DISTINCT C.comunityId) AS comunityIds,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM 
        Experiments AS E
    LEFT JOIN 
        BioReplicatesPerExperiment AS BRI ON E.experimentUniqueId = BRI.experimentUniqueId
    LEFT JOIN 
        BioReplicatesPerExperiment AS BR ON E.experimentUniqueId = BR.experimentUniqueId
    LEFT JOIN 
        Community AS C ON E.studyId = C.studyId
    LEFT JOIN 
        CompartmentsPerExperiment AS CP ON E.experimentUniqueId = CP.experimentUniqueId
    WHERE 
        E.studyId = {studyID}
        AND BR.controls = 1
    GROUP BY 
        E.experimentId,
        E.experimentUniqueId,
        E.experimentDescription,
        E.cultivationMode,
        E.controlDescription;
    """
    df_experiments = conn.query(query, ttl=600)
    columns_to_exclude = ['experimentUniqueId']
    return df_experiments.drop(columns=columns_to_exclude)

def getMicrobialStrains(studyID, conn):
    query = f"SELECT * FROM Strains WHERE studyId = {studyID};"
    df_Bacteria = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId']
    return df_Bacteria.drop(columns=columns_to_exclude)

def getCompartment(studyID, conn):
    query = f"SELECT DISTINCT * FROM Compartments WHERE studyId = {studyID};"
    df_Compartment = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId','compartmentUniqueId']
    return df_Compartment.drop(columns=columns_to_exclude)

def getMetabolite(studyID, conn):
    query = f"SELECT * FROM MetabolitePerExperiment  WHERE studyId = {studyID};"
    df_Metabolite = conn.query(query, ttl=600)
    columns_to_exclude = ['experimentUniqueId','experimentId','bioreplicateUniqueId']
    return df_Metabolite.drop(columns=columns_to_exclude)

def getPerturbations(studyID, conn):
    query = f"SELECT * FROM Perturbation WHERE studyId = {studyID};"
    df_perturbations = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId', 'perturbationUniqueid']
    return df_perturbations.drop(columns=columns_to_exclude)

def getCommunities(studyID, conn):
    query = f"""
    SELECT 
        C.comunityId,
        GROUP_CONCAT(DISTINCT S.memberName) AS memberNames,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM 
        Community AS C
    LEFT JOIN 
        Strains AS S ON C.strainId = S.strainId
    LEFT JOIN 
        CompartmentsPerExperiment AS CP ON CP.comunityUniqueId = C.comunityUniqueId
    WHERE 
        C.studyId = {studyID}
    GROUP BY 
        C.comunityId;
    """
    df_communities = conn.query(query, ttl=600)
    #columns_to_exclude = ['studyId', 'perturbationUniqueId']
    return df_communities

def getBiorep(studyID, conn):
    query = f"""
    SELECT 
        B.bioreplicateId,
        B.bioreplicateUniqueId,
        B.controls,
        B.OD,
        B.Plate_counts,
        B.pH,
        BM.biosampleLink,
        BM.bioreplicateDescrition
    FROM 
        BioReplicatesPerExperiment AS B
    LEFT JOIN 
        BioReplicatesMetadata AS BM ON B.bioreplicateUniqueId = BM.bioreplicateUniqueId
    WHERE 
        B.studyId = {studyID};
        """
    df_bioreps = conn.query(query, ttl=600)
    columns_to_exclude = ['bioreplicateUniqueId']
    return df_bioreps.drop(columns=columns_to_exclude)

def getAbundance(studyID, conn):
    query = f"""
    SELECT 
        A.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM 
        Abundances AS A
    JOIN 
        Strains AS S ON A.strainId = S.strainId
    WHERE 
        A.studyId = {studyID};
        """
    df_abundances = conn.query(query, ttl=600)
    return df_abundances

def getFC(studyID, conn):
    query = f"""
    SELECT 
        F.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM 
        FC_Counts AS F
    JOIN 
        Strains AS S ON F.strainId = S.strainId
    WHERE 
        F.studyId = {studyID};
        """
    df_FC = conn.query(query, ttl=600)
    return df_FC

def dynamical_query(all_advance_query):
    base_query = "SELECT DISTINCT studyId"
    search_final_query =  ""
    for query_dict in all_advance_query:
        where_clause = ""
        if query_dict['option']:
            if query_dict['option'] == 'Project Name':
                project_name = query_dict['value']
                if project_name !=  '':
                    where_clause = f"""
                    FROM Study
                    WHERE projectUniqueID IN (
                        SELECT projectUniqueID
                        FROM Project
                        WHERE projectName LIKE '%{project_name}%'
                        )
                    """
            elif query_dict['option'] == 'Project ID':
                project_id = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE projectUniqueID IN (
                    SELECT projectUniqueID
                    FROM Project
                    WHERE projectId = '{project_id}'
                    )
                """
            elif query_dict['option'] == 'Study Name':
                study_name = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE studyName LIKE '%{study_name}%'
                """
            elif query_dict['option'] == 'Study ID':
                study_id = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE studyId = '{study_id}'
                """
            elif query_dict['option'] == 'Microbial Strain':
                microb_strain = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE memberName LIKE '%{microb_strain}%'
                """
            elif query_dict['option'] == 'NCBI ID':
                microb_ID = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE NCBId = '{microb_ID}'
                """
            elif query_dict['option'] == 'Metabolites':
                metabo = query_dict['value']
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE metabo_name LIKE '%{metabo}%'
                """
            elif query_dict['option'] == 'chEBI ID':
                cheb_id = query_dict['value']
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE cheb_id = '{cheb_id}'
                """  
            elif query_dict['option'] == 'pH':
                start, end = query_dict['value']
                where_clause = f"""
                FROM Compartments
                WHERE initialPh BETWEEN {start} AND {end}
                """
        logic_add = ""
        if 'logic_operator' in query_dict:
            if query_dict['logic_operator'] == 'AND':
                logic_add = " AND studyId IN ("
            if query_dict['logic_operator'] == 'OR':
                logic_add = " OR studyId IN ("
            if query_dict['logic_operator'] == 'NOT':
                logic_add = " AND studyId NOT IN ("
        
        if logic_add != "":
            final_query = logic_add + " " + base_query + " " + where_clause + " )"
        else:
            final_query = base_query + " " + where_clause + " "
        
        search_final_query += final_query
    
    search_final_query = search_final_query + ";"
    return search_final_query


if search_button or st.session_state.form:
    st.session_state.form = True

    final_query = dynamical_query(all_advance_query)
    print(final_query)

    conn = st.connection("BacterialGrowth", type="sql")
    df_studies = conn.query(final_query, ttl=600)

    

    num_results = len(df_studies)

    if num_results == 0:
        st.warning("Sorry, there is no studies in the database that match your search.")
    
    else:

        st.write(f'**{num_results}** search results')

        with st.form(key="Results"):
            c1 , c2 = st.columns([0.05, 0.95])
            for i in range(len(df_studies)):
                with c1:
                    down_check = st.checkbox(f"{i+1}",key=f'checkbox{i}')

                with c2:
                    df_general = getGeneralInfo(df_studies['studyId'][i], conn)
                    study_name = df_general['studyName'][i]
                    transposed_df = df_general.T
                    studyname = st.page_link("pages/3_Upload Data.py",label= f':blue[**{study_name}**]')
                    formatted_html = transposed_df.to_html(render_links=True, escape=False, justify='justify', header = False)
                    styled_html = f"<style>table {{ font-size: 13px; }}</style>{formatted_html}"
                    table = st.markdown(styled_html, unsafe_allow_html=True)

                    space = st.text("")

                    with st.expander("**Experiments**"):
                        df_experiments = getExperiments(df_studies['studyId'][i], conn)
                        st.dataframe(df_experiments,hide_index=True,)

                    space = st.text("")
                    
                    with st.expander("**Compartments**"):
                        df_Compartment = getCompartment(df_studies['studyId'][i], conn)
                        st.dataframe(df_Compartment,hide_index=True,)
                    
                    space = st.text("")
                    
                    with st.expander("**Microbial Strains and Communities**"):
                        df_Compartment = getCommunities(df_studies['studyId'][i], conn)
                        st.dataframe(df_Compartment,hide_index=True,)
                        df_strains = getMicrobialStrains(df_studies['studyId'][i], conn)
                        st.dataframe(df_strains,hide_index=True,)


                    space = st.text("")
                    
                    with st.expander("**Biological Replicates, Growth and Metabolites Measurements**"):
                        df_biorep = getBiorep(df_studies['studyId'][i], conn)
                        st.dataframe(df_biorep,hide_index=True,)
                        df_abundance = getAbundance(df_studies['studyId'][i], conn)
                        st.dataframe(df_abundance,hide_index=True,)
                        df_FC = getFC(df_studies['studyId'][i], conn)
                        st.dataframe(df_FC,hide_index=True,)
                        df_Metabolite = getMetabolite(df_studies['studyId'][i], conn)
                        st.dataframe(df_Metabolite,hide_index=True,)


                    space = st.text("")

                    with st.expander("**Perturbations**"):
                        df_perturbation = getPerturbations(df_studies['studyId'][i], conn)
                        st.dataframe(df_perturbation,hide_index=True,)
                    
            space2 = st.text("")
            download = st.form_submit_button("Dowload Data", type = 'primary')
            if download:
                st.write('bla')
        
'''

conn = st.connection("BacterialGrowth", type="sql")

# Perform query.
df_study = conn.query('SELECT * from Study;', ttl=600)
st.dataframe(df_study)

df_biologicalrep = conn.query('SELECT * from Experiments;', ttl=600)
st.dataframe(df_biologicalrep)

df_technicalrep = conn.query('SELECT * from Compartments;', ttl=600)
st.dataframe(df_technicalrep)

df_ReactorSetUp = conn.query('SELECT * from Strains;', ttl=600)
st.dataframe(df_ReactorSetUp)

df_Compartments = conn.query('SELECT * from Community;', ttl=600)
st.dataframe(df_Compartments)

df_Bacteria = conn.query('SELECT * from CompartmentsPerExperiment;', ttl=600)
st.dataframe(df_Bacteria)

df_metabolites = conn.query('SELECT * from TechniquesPerExperiment;', ttl=600)
st.dataframe(df_metabolites)

df_metabolitesyn = conn.query('SELECT * from BioReplicatesPerExperiment;', ttl=600)
st.dataframe(df_metabolitesyn)

df_metabolite_repl = conn.query('SELECT * from Perturbation;', ttl=600)
st.dataframe(df_metabolite_repl)

df_metabolitedb = conn.query('SELECT * from Metabolites;', ttl=600)
st.dataframe(df_metabolitedb)

df_Abundances = conn.query('SELECT * from Abundances;', ttl=600)
st.dataframe(df_Abundances)

df_FC_couts = conn.query('SELECT * from FC_Counts;', ttl=600)
st.dataframe(df_FC_couts)

df_BioReplicatesMetadata = conn.query('SELECT * from BioReplicatesMetadata', ttl=600)
st.dataframe(df_BioReplicatesMetadata)

df_MetabolitePerReplicates = conn.query('SELECT * from MetabolitePerExperiment;', ttl=600)
st.dataframe(df_MetabolitePerReplicates)


#st.markdown("# Search")
#st.write(
#    '''


