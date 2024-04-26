import streamlit as st
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components
#from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

st.set_page_config(page_title="Database Search", page_icon="🔍", layout='wide')

add_logo("logo_sidebar2.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


# Add a title to your Streamlit app
st.image('pages/SearchBanner.png')
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
options = ['Study Name', 'Organism', 'Metabolites', 'chEBI ID', 'pH']
options_logical = ['AND', 'OR', 'NOT']

# Define the range for the slider
min_value_ph = 0.0
max_value_ph = 14.0
min_value_ph_add = 0.0
max_value_ph_add = 14.0

if 'rows' not in st.session_state:
    st.session_state['rows'] = 0

def increase_rows():
    st.session_state['rows'] += 1

def decrease_rows():
    st.session_state['rows'] -= 1

# Use columns to lay out the elements side by side
col1, col2 = st.columns([1, 2])

# Add a text input field to the first column
with col1:
    selected_option = st.selectbox('Select an option:', options, key='selectbox1')

# Add a selectbox to the second column
with col2:
    if selected_option == 'pH':
        start_value, end_value = st.slider('Select a range:', min_value_ph, max_value_ph, (min_value_ph, max_value_ph), step=0.5, key='range1', format="%.1f")
    else:
        input_value = st.text_input('Enter Text here:', '', key='textinput1')

st.button('Advanced Search', on_click=increase_rows)

# Function to render additional dropdown block
def display_bar_row(index):

    col1_add, col2_add, col3_add = st.columns([1, 1, 2])
    # Add a text input field to the first column
    with col1_add:
        logical_options = st.selectbox('Select logic opetator:', options_logical, key=f'box1_add{index}')

    with col2_add:
        selected_option_add = st.selectbox('Select an option:', options,  key=f'box2_add{index}')

    with col3_add:
        if selected_option_add == 'pH':
            start_value_add, end_value_add = st.slider('Select a range:', min_value_ph_add, max_value_ph_add, (min_value_ph_add, max_value_ph_add), step=0.5, key=f'slide1_add{index}', format="%.1f")
        else:
            input_value_add = st.text_input('Enter Text here:', '', key=f'text1_add{index}')

    col4_add, col5_add = st.columns([0.5, 0.5])
    with col4_add:
        st.button('Add More',key=f'add1_button_{index}', on_click=increase_rows)

    with col5_add:
        st.button('Delete',key=f'add2_button_{index}', on_click=decrease_rows)

for i in range(st.session_state['rows']):
    display_bar_row(i)

search_button = st.button('**Search Data**',type='primary')

st.text("")
st.text("")

if "form" not in st.session_state:
    st.session_state.form = False


def getBacteria(studyID):
    conn = conn = st.connection("BacterialGrowth", type="sql")
    query = f"SELECT DISTINCT Bacteria.* FROM Bacteria JOIN BacteriaCommunity ON Bacteria.bacteriaId = BacteriaCommunity.bacteriaId JOIN BiologicalReplicate ON BacteriaCommunity.biologicalReplicateId = BiologicalReplicate.biologicalReplicateId WHERE BiologicalReplicate.studyId = {studyID};"
    df_Bacteria = conn.query(query, ttl=600)
    columns_to_display = ['bacteriaGenus', 'bacteriaSpecies','bacteriaNCBISpeciesID','bacteriaStrain','bacteriaNCBIStrainID']
    return df_Bacteria[columns_to_display]

def getReactor(studyID):
    conn = conn = st.connection("BacterialGrowth", type="sql")
    query = f"SELECT DISTINCT rs.* FROM ReactorSetUp rs JOIN BiologicalReplicate br ON rs.reactorSetUpId = br.reactorSetUpId JOIN Study s ON br.studyId = s.studyId WHERE s.studyId = {studyID};"
    df_Reactor = conn.query(query, ttl=600)
    columns_to_display = ['reactorSetUpName', 'reactorSetUpMode','reactorSetUpDescription']
    return df_Reactor[columns_to_display]

def getCompartment(studyID):
    conn = conn = st.connection("BacterialGrowth", type="sql")
    query = f"SELECT DISTINCT c.* FROM Compartments c JOIN ReactorSetUp rs ON c.reactorSetUpId = rs.reactorSetUpId JOIN BiologicalReplicate br ON rs.reactorSetUpId = br.reactorSetUpId JOIN Study s ON br.studyId = s.studyId WHERE s.studyId = {studyID};"
    df_Compartment = conn.query(query, ttl=600)
    columns_to_display = ['compartmentName','reactorSetUpName', 'compartmentNumber','volume','pressure','stirring_speed','stirring_mode','O2','CO2','H2','N2','mediaName']
    return df_Compartment[columns_to_display]

def getMetabolite(studyID):
    conn = conn = st.connection("BacterialGrowth", type="sql")
    query = f"SELECT DISTINCT m.* FROM Metabolites m JOIN MetaboliteReplicates mr ON m.cheb_id = mr.cheb_id JOIN TechnicalReplicate tr ON mr.technicalReplicateId = tr.technicalReplicateId JOIN BiologicalReplicate br ON tr.biologicalReplicateId = br.biologicalReplicateId JOIN Study s ON br.studyId = s.studyId WHERE s.studyId = {studyID};"
    df_Metabolite = conn.query(query, ttl=600)
    columns_to_display = ['cheb_id','metabo_name']
    return df_Metabolite[columns_to_display]


if search_button or st.session_state.form:
    st.session_state.form = True
    conn = st.connection("BacterialGrowth", type="sql")
    query = f"SELECT * FROM Study WHERE studyName LIKE '%{input_value}%';"
    df_studyname = conn.query(query, ttl=600)

    transposed_df = df_studyname.T
    new_headers = ['Study Information']
    transposed_df.columns = new_headers

    num_results = len(df_studyname)

    st.write(f'**{num_results}** search results')

    with st.form(key="Results"):
        c1 , c2 = st.columns([0.1, 0.9])
        for i in range(len(df_studyname)):
            with c1:
                down_check = st.checkbox(f"{i+1}",key=f'checkbox{i}')

            with c2:
                study_name = df_studyname['studyName'][i]
                studyname = st.page_link("pages/2_Upload Data.py",label= f':blue[**{study_name}**]')
                formatted_html = transposed_df.to_html(render_links=True, escape=False, justify='justify', header = False)
                styled_html = f"<style>table {{ font-size: 13px; }}</style>{formatted_html}"
                table = st.markdown(styled_html, unsafe_allow_html=True)

                space = st.text("")
                space = st.text("")

                with st.expander("**Bacterial Community Information**"):
                    df_Bacteria = getBacteria(df_studyname['studyId'][i])
                    st.dataframe(df_Bacteria,hide_index=True,)

                space = st.text("")

                with st.expander("**Reactor Setup Information**"):
                    df_Reactor = getReactor(df_studyname['studyId'][i])
                    st.dataframe(df_Reactor,hide_index=True,)

                space = st.text("")

                with st.expander("**Compartement Information**"):
                    df_Compartment = getCompartment(df_studyname['studyId'][i])
                    st.dataframe(df_Compartment,hide_index=True,)

                space = st.text("")

                with st.expander("**Metabolite Information**"):
                    df_Metabolite = getMetabolite(df_studyname['studyId'][i])
                    st.dataframe(df_Metabolite,hide_index=True,)

                space = st.text("")
        space2 = st.text("")
        download = st.form_submit_button("Dowload Data", type = 'primary')
        space3 = st.text("")





conn = st.connection("BacterialGrowth", type="sql")

# Perform query.
df_study = conn.query('SELECT * from Study;', ttl=600)
st.dataframe(df_study)

df_biologicalrep = conn.query('SELECT * from Events;', ttl=600)
st.dataframe(df_biologicalrep)

df_technicalrep = conn.query('SELECT * from Compartments;', ttl=600)
st.dataframe(df_technicalrep)

df_ReactorSetUp = conn.query('SELECT * from Strains;', ttl=600)
st.dataframe(df_ReactorSetUp)

df_Compartments = conn.query('SELECT * from Community;', ttl=600)
st.dataframe(df_Compartments)

df_Bacteria = conn.query('SELECT * from CompartmentsPerEvent;', ttl=600)
st.dataframe(df_Bacteria)

df_metabolites = conn.query('SELECT * from TechniquesPerEvent;', ttl=600)
st.dataframe(df_metabolites)

df_metabolitesyn = conn.query('SELECT * from BioReplicatesPerEvent;', ttl=600)
st.dataframe(df_metabolitesyn)

df_metabolite_repl = conn.query('SELECT * from Perturbation;', ttl=600)
st.dataframe(df_metabolite_repl)

df_metabolitedb = conn.query('SELECT * from Metabolites;', ttl=600)
st.dataframe(df_metabolitedb)

df_Abundances = conn.query('SELECT * from Abundances;', ttl=600)
st.dataframe(df_Abundances)

df_MetabolitePerReplicates = conn.query('SELECT * from MetabolitePerEvent;', ttl=600)
st.dataframe(df_MetabolitePerReplicates)


#st.markdown("# Search")
#st.write(
#    """This demo illustrates a combination of plotting and animation with
#Streamlit. We're generating a bunch of random numbers in a loop for around
#5 seconds. Enjoy!"""
#)

# Print results.
#for row in df.itertuples():
#    st.write(f"{row.studyId} ID, Study Name: {row.studyName}, Study Description: {row.studyDescription} ")


