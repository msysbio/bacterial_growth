
import streamlit as st
from streamlit_extras.app_logo import add_logo
# from streamlit_tags import st_tags

from datetime import datetime, timedelta
import sys, os, re, time
import pandas as pd
import yaml

# Import custom methods
filepath = os.path.realpath(__file__)
root_dir = os.path.dirname(os.path.dirname(filepath))
relative_path_to_src = os.path.join(root_dir, 'src')
sys.path.append(relative_path_to_src)
from create_rawdata_excel import create_rawdata_excel_fun
from create_excel import create_excel_fun
from parse_ex_to_yaml import parse_ex_to_yaml
from constants import *
from check_yaml import test_study_yaml, test_experiments_yaml, test_compartments_yaml, test_comu_members_yaml, test_communities_yaml, test_perturbation_yaml
from populate_db_mod import populate_db, generate_unique_id
import db_functions as db
from parse_raw_data import save_data_to_csv


# Page config
st.set_page_config(page_title="Upload Data", page_icon="📤", layout='wide')





add_logo("figs/logo_sidebar3.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.image('figs/UploadBanner.png')

# Static part
css = '''
<style>
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.6rem;
    font-weight: bold;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)
st.markdown("![badge](https://img.shields.io/badge/status-under%20development-orange?style=for-the-badge)")
st.markdown(
    """
    Thank you for choosing to share your microbial growth data with us. Your commitment to sharing experimental data is essential
    for advancing our understanding of microbiome dynamics. Your contribution plays a vital role in driving research forward and enhancing
    our collective knowledge in this field.

    To successfully submit your data, please ensure that you follow the instructions provided in each of the following steps. Adhering to these
    instructions helps us maintain the quality of our database and ensures the accuracy and reliability of the information stored within it.
    Thank you for your cooperation in maintaining data integrity and reliability.
    """
)

st.write('')
st.write('')


# Dynamic part

global unique_community_ids
global list_selected_microbes
global list_strains
list_strains = []
list_selected_microbes = []
data_excel = None

tab1, tab2,  tab3, tab4, tab5 = st.tabs(["Step 1", "Step 2","Step 3", "Step 4", "Step 5"])

unique_community_ids = set()
conn = st.connection("BacterialGrowth", type="sql")

if 'rows_communities' not in st.session_state:
    st.session_state['rows_communities'] = {}
    st.session_state['rows_communities'][1] = True

if 'private_project_id' not in st.session_state:
    st.session_state['private_project_id'] = None


def is_valid_email(email):
    # Regular expression pattern for validating email addresses
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def increase_rows():
    index = len(st.session_state['rows_communities'])
    st.session_state['rows_communities'][index + 1] = True


def decrease_rows(index):
    keys_to_remove = []
    for key in st.session_state:
        if key.endswith(str(index)):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del st.session_state[key]


def toggle_container(index):
    st.session_state['rows_communities'][index] = not st.session_state['rows_communities'][index]

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

@st.cache_data
def taxonomy_df_for_taxa_list(taxa_list, _conn):
    # """
    # Using an already established connection to the db, get a dataframe with hits for a list of taxa.
    # NOTE: Remebmer that it takes a list as input, thus if you are about to query for a single term, make a list with sole element.
    # ""
    dfs = []
    for taxon in taxa_list:
        if taxon == "":
            continue
        tax_query = f"SELECT * FROM Taxa WHERE tax_names LIKE '%{taxon}%';"
        df_taxonomy = _conn.query(tax_query, ttl=None)
        dfs.append(df_taxonomy)
    return pd.concat(dfs, ignore_index=True)


def display_strain_row(index):
    # """
    # Add 4-cols template for addin a new strain without an NCBI Taxonomy Id when other_strains is "No"
    # """
    row_strain_data = {}

    if index not in st.session_state['rows_communities']:
        pass

    elif st.session_state['rows_communities'][index]:

        with st.container():

            if f'add_button_clicked_{index}' not in st.session_state:
                st.session_state[f'add_button_clicked_{index}'] = False

            if f'delete_button_clicked_{index}' not in st.session_state:
                st.session_state[f'delete_button_clicked_{index}'] = False

            # Add a text input field to the first column  --  columns for unknown taxa (no NCBI Tax Id available)
            col1_add, col2_add = st.columns(2)
            with col1_add:
                other_name = st.text_input(
                    '*Name of the microbial strain:',
                    placeholder='1. Provide a name to the microbial strain',
                    help='Complete with the name of your microbial strain that does not match to an existing NCBI Taxonomy Id.',
                    key=f'other_name_{index}'
                )
                row_strain_data['name'] = other_name

            with col2_add:
                other_description = st.text_input(
                    '*Description of the microbial strain:',
                    placeholder='2. Provide an informative desciption of the microbial strain',
                    help='Complete with a description of your microbial strain',
                    key=f'other_description_{index}'
                )
                row_strain_data['description'] = other_description

            # Columns for taxa with NCBI Tax Id available
            col3_add, col4_add, col6_add= st.columns([0.39, 0.39, 0.10])
            info = []
            warning = []
            with col3_add:
                input_other_taxa = st.text_input(
                    '*Search microbial strain species:',
                    placeholder='3. Search microbial strain species',
                    help='Type the specific microbial strain  species, then press enter',
                    key=f'input_other_taxa_{index}'
                )

            with col4_add:
                if input_other_taxa:
                    df_other_taxonomy = taxonomy_df_for_taxa_list([input_other_taxa], conn)
                    df_taxa_other_name = df_other_taxonomy['tax_names']
                    other_taxonomy = st.selectbox(
                        '*Select microbial strain species',
                        options=df_taxa_other_name,
                        index=None,
                        placeholder="4. Select one of the species below",
                        help='Select only one microbial strain species, then click on add',
                        key=f'other_taxonomy_{index}'
                    )
                    if other_taxonomy is not None:
                        if other_name == "":
                            warning.append("Please make sure you provide a name before you continue.")
                        if other_description == "":
                            warning.append("Please make sure you provide a description to before you continue.")

                        row_strain_data["case_number"] = index
                        row_strain_data['parent_taxon'] = other_taxonomy
                        row_strain_data['parent_taxon_id'] = df_other_taxonomy[
                                    df_other_taxonomy["tax_names"] == other_taxonomy
                                    ]["tax_id"].item()

                        parent_strains_df = taxonomy_df_for_taxa_list([other_taxonomy], conn)
                        strains_df = parent_strains_df[ parent_strains_df['tax_names'] == other_taxonomy ]
                        taxa_id = strains_df.iloc[0]['tax_id']
                        row_strain_data['parent_taxon_id'] = taxa_id

                        info.append(
                            f'For more information about **{other_taxonomy}** go to the \
                                NCBI Taxonomy ID:[{taxa_id}](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={taxa_id})'
                        )
            if warning:
                for i in warning:
                    st.warning(i)
            if info:
                for j in info:
                    st.info(j)

        # Buttons
        with col6_add:
            st.write("")
            st.write("")


            if f'delete_button_visible_{index}' not in st.session_state:
                st.session_state[f'delete_button_visible_{index}'] = True

            if st.session_state[f'delete_button_visible_{index}']:
                if st.button('Delete',
                             key=f'delete_button_{index}',
                             type='primary',
                             on_click=lambda: toggle_container(index)):
                     st.session_state[f'delete_button_visible_{index}'] = False

    return row_strain_data


if 'verify' not in st.session_state:
    st.session_state['verify'] = 0


def update_verify():
    st.session_state['verify'] = 1


def create_StudyID():
    st.success("Your Study ID is 123456789, copy this number somewhere safe since you will need to upload new versions in the future")
    st.info("Now go to Step 2 and folow the instructions")


def tab_step1():

    create_private_project_id = None
    unique_study_id_val = None
    project_name = None
    project_description = None


    # Step 1: set type of data submission
    with tab1:
        st.subheader("1. Select type of data submission")
        st.markdown(
            """
            **Data Submission Options:**
            - [x] **Add a new study to a new project:** Choose this option if you're uploding study data from a new, non existing project.
            - [x] **Add a new study to a previous project:** Choose this option if you're updating a new study to an already existing project.
            - [x] **Add a new version of a study to a previous project:** Choose this option if you're updating a new study version to an already existing project.

            **Private study ID:** Please provide the unique study ID of the previous study you wish to update. This ensures continuity and helps us maintain the database up to data.

            **Private project ID:** Please provide the unique project ID of the existing project where you wish to add a new study or update a previous created study.

            If you do not remember the unique IDs please follow the intructions in (link).
            """)

        options = ['Add a new study to a new project','Add a new study to a previous project','Add a new version of a study to a previous project']
        new_ckeck = st.selectbox('Select the type of data submission:',
                                 options,
                                 None,
                                 help='Choose one of the options for your data submission.'
                    )

        # NEW PROJECT
        if new_ckeck == 'Add a new study to a new project':
            col1, col2 = st.columns([0.87,0.13])
            with col1:
                project_name = st.text_input('Project name:',help='Name the new project',placeholder='1. Provide a name for your new project')
                project_description = st.text_input('Project description:',help='Description the new project',placeholder='2. Provide a project description')
                st.session_state.dontCreate = (project_name == "" or project_description == "")

            with col2:
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')


                create_button = st.button("Create project", disabled = st.session_state.dontCreate, type="primary")


            if st.session_state['private_project_id'] is None:
                create_private_project_id = generate_unique_id()
                st.session_state['private_project_id'] = create_private_project_id

            if st.session_state['private_project_id'] is not None:
                create_private_project_id = st.session_state['private_project_id']


            if create_button:

                # if st.session_state['private_project_id'] is None:
                #     create_private_project_id = generate_unique_id()
                #     st.session_state['private_project_id'] = create_private_project_id

                # if st.session_state['private_project_id'] is not None:
                #     create_private_project_id = st.session_state['private_project_id']


                update_verify()

                st.info(f"""Your New proyect **{project_name}** was successfully created! \
                    Your **Private Proyect ID** is **{create_private_project_id}**.  \
                    Copy and paste somewhere safe this ID, you will need it to upload more studies or do updates. \
                    Go to **Step 2** and folow the instructions!""", icon="✅"
                )
                # [TODO] then verify that the number is correct

        # NEW STUDY ON ONGOING PROJECT
        if new_ckeck == 'Add a new study to a previous project':
            col1, col2 = st.columns([0.85,0.15])
            with col1:
                project_id = st.text_input(
                    'Project unique ID:',
                    help='Provide the unique ID of the project you want to add a new study',
                    placeholder='1. Provide the unique project ID'
                )
                st.session_state.dontAdd = project_id == ""
            with col2:
                st.write('')
                st.write('')
                verify_button = st.button("Verify unique ID", disabled=st.session_state.dontAdd, type="primary")

            if verify_button and project_id:
                df_proyect_id = db.getPrivateProjectID(project_id,conn)
                if not df_proyect_id.empty:
                    project_info_df = db.getProjectInfo(project_id, conn)
                    project_name = project_info_df['projectName'][0]
                    project_description = project_info_df['projectDescription'][0]
                    update_verify()
                    st.info(f"Go to **Step 2** and folow the instructions!", icon="✅")
                else:
                    st.warning("Incorrect Private Project ID, try again.")

        print( st.session_state['verify'] )

        # UPDATE STUDY
        if new_ckeck == 'Add a new version of a study to a previous project':
            col1, col2 = st.columns([0.8,0.2])
            with col1:
                project_id = st.text_input(
                    'Project unique ID:',
                    help='Provide the unique ID of the study project you want to add a new version',
                    placeholder='1. Provide the unique project ID'
                )
                study_id = st.text_input(
                    'Study unique ID:',
                    help='Provide the unique ID of the study you want to add a new version',
                    placeholder='2. Provide the unique study ID'
                )
                st.session_state.dontUpdate = (project_id == "" or study_id == "")
            with col2:
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                verify2_button = st.button("Verify unique IDs", disabled=st.session_state.dontUpdate, type="primary")

            if verify2_button and project_id and study_id:
                df_proyect_id = db.getPrivateProjectID(project_id,conn)
                unique_project_id_val = df_proyect_id["projectUniqueID"][0]
                create_private_project_id = unique_project_id_val
                unique_study_id_val = df_proyect_id["studyUniqueID"][0]
                if not df_proyect_id.empty and unique_study_id_val == study_id:
                    project_info_df = db.getProjectInfo(project_id, conn)
                    project_name = project_info_df['projectName'][0]
                    project_description = project_info_df['projectDescription'][0]
                    update_verify()
                    st.info(f"Go to **Step 2** and folow the instructions!", icon="✅")
                else:
                    st.warning("Incorrect Private Project ID or Private Study ID, try again.")

    return create_private_project_id, unique_study_id_val, project_name, project_description


def tab_step2():
    # """
    # Main upload function:
    # invokes the display_strain_row() function for each new entry of novel taxa (without an NCBI Taxonomy Id.)

    # Returns:
    #     - keywords:         species names with exact NCBI Taxonomy Ids
    #     - list_taxa_id:     NCBI Taxonomy Ids of the keywords
    #     - all_strain_data:  species names that do not match to an exact NCBI Taxonomy Ids
    #     - other_taxa_list:  NCBI Taxonomy Ids of the parent taxa of the all_strain_data
    # """
    keywords = []
    all_strain_data = []
    list_taxa_id = []
    other_taxa_list = []

    if 'list_strains' not in st.session_state:
        st.session_state['list_strains'] = []

    if st.session_state.get('add'):
        val_taxonomy = st.session_state.get('select_taxa')
        if val_taxonomy:
            st.session_state.list_strains.append(val_taxonomy)
        st.session_state['input_taxa'] = ''
        st.session_state['select_taxa'] = None

    with tab2:

        if st.session_state['verify'] == 1:
            # """
            # Step 2: Describing the strains
            # """
            df_taxonomy = ""
            st.subheader("2. Select all the microbial strains used in the study")
            st.markdown(
                """
                Using the search tap bellow, select all the microbial strains used in your study as well as any uncultured communities, click on 'add' to include the selected option.
                If you do not find all of the microbial strains define you own by specifying its name and parent strain species. Once you are sure all the different community members are defined, click on 'save'.
                """
            )
            # Strains with NCBI Taxonomy Ids.
            col1, col2, col3 = st.columns([0.45,0.45,0.1])
            with col1:
                input_taxon = st.text_input(
                    'Search microbial strain:',
                    key = 'input_taxa',
                    placeholder='1. Search microbial strain',
                    help='Type the specific microbial strain, then press enter'
                )

            with col2:
                if input_taxon:
                    df_taxa_taxonomy = taxonomy_df_for_taxa_list([input_taxon], conn)
                    df_taxa_name = df_taxa_taxonomy['tax_names']
                    taxonomy = st.selectbox(
                        'Select microbial strain',
                        options=df_taxa_name,
                        index=None,
                        placeholder="2. Select one of the strains below",
                        key = 'select_taxa',
                        help='Select only one microbial strain, then click on add'
                    )
                    val_taxonomy = taxonomy

            with  col3:
                st.write("")
                st.write("")
                add_button = st.button('Add', key='add', type='primary')

            keywords = st.multiselect(
                label='Microbial species added',
                options=st.session_state.list_strains,
                default=st.session_state.list_strains
            )

            to_remove = [k for k in st.session_state.list_strains if k not in keywords]

            for k in to_remove:
                st.session_state.list_strains.remove(k)

            if len(keywords) > 0:
                temp_df = taxonomy_df_for_taxa_list(keywords, conn)

                for i in keywords:
                    list_taxa_id.append(temp_df[temp_df['tax_names'] == i].iloc[0]['tax_id'])
                    strains_df = temp_df[temp_df['tax_names'] == i]
                    taxa_id = strains_df.iloc[0]['tax_id']
                    st.info(f'For more information about **{i}** go to the NCBI Taxonomy ID:[{taxa_id}](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={taxa_id})',
                            icon="❕"
                    )

            other_strains = st.radio("*Did you find all the microbial strains?:",
                                ["Yes, all microbial strains used in my study have been added.",
                                    "No, Some microbial strains were not found"
                                    ],
                                    index=None
            )

            # All user's strains have NCBI Taxonomy Ids
            if other_strains == "Yes, all microbial strains used in my study have been added.":
                list_taxa_id = [temp_df[temp_df['tax_names'] == keyword].iloc[0]['tax_id'] for keyword in keywords]
                if len(list_taxa_id):
                    st.success("Done! Microbial strains saved, then go to **Step 3**", icon="✅")

            # Case where a strain does not correspond to a NCBI Taxonomy Id
            elif other_strains == "No, Some microbial strains were not found":

                # Parse all novel strains (without a NCBI Taxonomy Id) added
                for i in range(1, len(st.session_state['rows_communities']) + 1):
                    st.write('')
                    strain_data = display_strain_row(i)
                    all_strain_data.append(strain_data)

                st.button('Add More',
                        key=f'add_button_{i}',
                        type='primary',
                        on_click=increase_rows
                )

                # Save both novel and strains with NCBI Taxonomy Ids
                save_all = st.button('Save All', type='primary')
                if save_all:

                    # Check if there are strains that do have exact NCBI Taxonomy ids.
                    if len(keywords) > 0:
                        df_taxonomy = taxonomy_df_for_taxa_list(keywords, conn)
                        list_taxa_id = [df_taxonomy[df_taxonomy['tax_names'] == keyword].iloc[0]['tax_id'] for keyword in keywords]

                    all_strain_data_del_in = all_strain_data.copy()
                    all_strain_data = []

                    for index, strain in enumerate(all_strain_data_del_in,  start=1):

                        if 'parent_taxon_id' not in strain:
                            continue

                        if st.session_state['rows_communities'][index]:
                            taxa_id =  strain['parent_taxon_id']
                            other_taxa_list.append(taxa_id)
                            all_strain_data.append(strain)

                    print("\n=======\n New round with: ")
                    print("keywords:", keywords)
                    print("list_taxa_id:", list_taxa_id)
                    print("other_taxa_list", other_taxa_list)
                    print("all_strain_data:", all_strain_data)

                    st.success("Done! Microbial strains saved, then go to **Step 3**", icon="✅")

        else:
            st.warning("Go back to Step 1 and fill in the details!", icon="⚠️")

    return keywords, list_taxa_id, all_strain_data, other_taxa_list


def tab_step3(keywords, list_taxa_id, all_strain_data,create_private_project_id, unique_study_id_val):
    # """
    # Step 3: Download templates tab
    # """
    metabo_col = []
    measure_tech = []
    all_taxa = []
    growth_techniques = GrowthTechniques()
    vessels = Vessels()

    with tab3:

        colu1,  colu2 = st.columns(2)

        if st.session_state['verify'] == 1:

            with colu1:


                st.subheader("1. Download the Data Template")
                st.markdown(
                    """
                    To ensure accurate data uploading, please follow these steps and fill in the provided data template according to your study setup:

                    - **Provide Study Information**: Select the type of vessels used and specify the number of vessels, columns, rows, and measurement time-points per experiment.

                    - **Select Growth Measurement Techniques**: Ensure to select all techniques used for growth measurement in your experiments.

                    - **Select Metabolites (Optional)**: If metabolites were measured in your experiments, select the relevant ones from the dropdown menu. You can also find more information about each metabolite by clicking on its CheBI ID link.
                    In case of not finding an specific metabolite, choose the closest one from the list and look in the incomming terms. For more information visit [ChEBI website](https://www.ebi.ac.uk/chebi/#)

                    - **Download Data Template**: Once all the require fields are completed, click on the button below to download the data template in Excel format. Fill in the template with your raw data accordingly.
                    """)

                # Set-up
                colu11, colu22 = st.columns(2)

                number_vessels = 0
                number_columns = 0
                number_rows = 0

                with colu11:
                    type_vessel = st.selectbox(
                        '*Select the type of vessels used:',
                        [ vessels.__getattribute__(x) for x in dir(vessels) if not x.startswith("_") ],
                        index=None,
                        help='Choose which type of vessel was used in your study'
                    )

                with colu22:
                    if type_vessel == vessels.bottles or type_vessel == vessels.agar_plates:
                        number_vessels = st.text_input(
                            '*Number of bottles/agar-plates:',
                            help='Please specify the total number of individual bottle or agar-plates in your study.',
                            value=0
                        )
                    else:
                        number_columns = st.text_input(
                            '*Number of columns:',
                            help='Please specify the number of columns in the well-plate or mini-bioreactor utilized in your study.',
                            value=0
                        )
                        number_rows = st.text_input(
                            '*Number of rows:',
                            help='Please specify the number of rows in the well-plate or mini-bioreactor utilized in your study.',
                            value=0
                        )

                # Time points
                number_timepoints = st.text_input(
                    '*Number of measurement time-points:',
                    help='Please provide the number of measurement time-points per experiment. If different time-points were used across experiments, please specify the largest one.'
                )

                # Techniques
                measure_tech = st.multiselect(
                    '*Select the techniques used to measure growth:',
                    [ growth_techniques.__getattribute__(x) for x in dir(growth_techniques) if not x.startswith("_") ],
                    help='Select all the measurement techniques used in your study to quantify bacterial growth.'
                )

                # Provide metabolites measured
                conn = st.connection("BacterialGrowth", type="sql")
                df_metabolites = conn.query('SELECT * from Metabolites;', ttl=None)
                df_metabo_name = df_metabolites['metabo_name']
                metabo_col = st.multiselect(
                    'If metabolites were measured, select which ones:',
                    df_metabo_name,
                    help='Select all the metabolites quantified in your study, please make sure to use the correct name.'
                )

                if metabo_col:
                    for i in metabo_col:
                        filtered_df = df_metabolites[df_metabolites['metabo_name'] == i]
                        cheb_id = filtered_df.iloc[0]['cheb_id']
                        st.info(f'For more information about **{i}** go to [{cheb_id}](https://www.ebi.ac.uk/chebi/searchId.do?chebiId={cheb_id})', icon="❕")

                # [NOTE] Keep
                all_taxa = []
                for case in all_strain_data:
                    if "case_number" in case:
                        # index = case["case_number"]
                        check = 'parent_taxon'
                        if check in case:
                            # parent_name = case['parent_taxon']
                            name = case['name']
                            all_taxa.append(name)

                if len(all_taxa) > 0:
                    all_taxa.extend(keywords)
                else:
                    all_taxa = keywords

                excel_rawdata = create_rawdata_excel_fun(measure_tech,
                                                         metabo_col,
                                                         type_vessel,
                                                         number_vessels,
                                                         number_columns,
                                                         number_rows,
                                                         number_timepoints,
                                                         all_taxa
                                )
                disabled = not measure_tech

                st.text('')
                st.text('')
                down_button = st.download_button(label='Click here to Download the Data Template',
                                    data=excel_rawdata,
                                    file_name='raw_data_template.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                    type="primary",
                                    use_container_width = True,
                                    disabled=disabled
                                    )
                if down_button:
                    with st.spinner('Downloading file'):
                        time.sleep(2)
                        st.success("Done! Complete file, then go to **Download the Study Template**", icon="✅")

            with colu2:
                st.subheader("2. Download the Study Template")
                st.markdown(
                    """
                    Click in the button to download the study template Excel file. The file contains four sheets:
                    - **README:** Read first before complete the other sheet. This provides detailed instruction for each of the columns in every of the following sheets.
                    - **STUDY:** In this sheet you will have to complete the basic information of the Study you are about to upload.
                    - **EXPERIMENTS** In this sheet you will complete all the details of each of the experiments in your study. Each row represent an **Experiment** and each column specific information about it. Fill as many rows as many different experiments you have in your study. **ORANGE COLUMNS** are present in other sheets and should be completed with the same values.
                    - **COMPARTMENTS:** Details of the different compartments used for the experiments. If identical conditions across different experiments occur, these should be considered as a single compartment as long as they used the same microbial community. So complete as many rows as different conditions setups you have among the experiments in your study (**EXPERIMENTS** rows).
                    - **COMMUNITY_MEMBERS:** Information with respect to the various strains used in this study. This tab will be dynamically generated. Please used the same Member_IDs in the **COMMUNITIES**.
                    _ **COMMUNITIES:** Define all the different communities used in your study by using the Member_IDs given in the **COMMUNITY_MEMBERS** sheet.
                    - **PERTURBATIONS:** In this sheet you will fill all the information related to the different perturbations made to an experiment (**Experiment_ID**). There are two types of perturbations possible: when altering compartment conditions such as: pH, temperature etc. or when adding new microbial **COMMUNITIES** like: environmental samples or new microvial strains.
                    Complete each section carefully according to the instructions. **DO NOT** modify the file by adding or deleating columns.
                    """)


                filtered_strains = [entry for entry in all_strain_data if entry and 'case_number' in entry]

                try:
                    excel_data = create_excel_fun(keywords, list_taxa_id, filtered_strains, create_private_project_id, unique_study_id_val)

                except:
                    print("Excel fails with")
                    print("keywords:", keywords)
                    print("list_taxa_id:", list_taxa_id)
                    print("all_strain_data:", filtered_strains)
                    print("=======")


                down_study_button = st.download_button(label='Click here to Download the Study Template',
                                                       data=excel_data,
                                                       file_name='study_template.xlsx',
                                                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                                       type="primary",
                                                       use_container_width = True
                                                       )
                if down_study_button:
                    with st.spinner('Downloading file'):
                        time.sleep(2)
                        st.success("Done! Complete file, then go to **Step 3**", icon="✅")

        else:
            st.warning("Go back to Step 1 and fill in the details!", icon="⚠️")
    return measure_tech, metabo_col, all_taxa


def tab_step4():
    xls_1 = None
    xls_2 = None
    with tab4:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. Upload Data Template")
            st.markdown(
            """
            Upload below the Excel Data file once completed with all the data measured in your
            study according to the instructions provided in the **Step 3**. Remember that no modifications are allowed after
            you submit the data. Please double check below that all the celds are correct.
            """)
            uploaded_file = st.file_uploader("Upload data file .xlsx here:", help='Only one .xlsx file allowed')

            if uploaded_file is not None:

                # Read the Excel file
                xls_1 = pd.ExcelFile(uploaded_file)

                # Get sheet names
                sheet_names = xls_1.sheet_names

                # Display sheet selection dropdown
                selected_sheet = st.selectbox("Select the Excel sheet you want to visualize", sheet_names)

                # Read the selected sheet
                df = pd.read_excel(xls_1, engine='openpyxl', sheet_name=selected_sheet)

                # Display the DataFrame
                st.dataframe(df)

        with col2:
            st.subheader("2. Upload Study Template")
            st.markdown(
            """
            Upload below the Excel Study file once completed with all the data measured in your
            study according to the instructions provided in the **Step 3**. Remember that no modifications are allowed after
            you submit the data. Please double check below that all the celds are correct.
            """)

            uploaded_file_2 = st.file_uploader("Upload study file .xlsx here:",help='Only one .xlsx file allowed')

            if uploaded_file_2 is not None:

                # Read the Excel file
                xls_2 = pd.ExcelFile(uploaded_file_2)

                # Get sheet names
                sheet_names = xls_2.sheet_names

                # Display sheet selection dropdown
                selected_sheet_2 = st.selectbox("Select the Excel sheet you want to visualize", sheet_names, key='box_2')

                # Read the selected sheet
                df_2 = pd.read_excel(xls_2, engine='openpyxl', sheet_name=selected_sheet_2)

                # Display the DataFrame
                st.dataframe(df_2)

                df_experimnets = pd.read_excel(xls_2, engine='openpyxl', sheet_name='EXPERIMENTS')

                global unique_community_ids
                unique_community_ids = set()
                for ids in df_experimnets['Community_ID']:
                    if ',' in ids:
                        unique_community_ids.update(id.strip() for id in ids.split(','))
                    else:
                        unique_community_ids.add(ids.strip())

        st.session_state.hinderUploading = (uploaded_file is None or uploaded_file_2 is None)

        submit_button = st.button("Save uploaded files", disabled=st.session_state.hinderUploading, type="primary", use_container_width = True)
        st.info(" Verify that all the data and study information are correct! \
                   No modifications to the data after uploaded are allowed.", icon="⚠️")
        # st.info("After checking that all the data provided is correct, click on **Save uploaded files**.")

        if submit_button:
            st.success("Done! Now go to **Step 5** and fill in the details.", icon="✅")
    return xls_1, xls_2


def tab_step5(xls_1, xls_2, measure_tech, metabo_col, all_taxa, conn, project_name, project_description):
    # """
    # Submit data page
    # """
    with tab5:
        st.subheader("Data visibility")
        st.write("By default your data will be visible and public in the database. Do you want to make your data visible now?")
        visibility_option = st.radio("Visibility options:",
                                   ["Yes, make my data visible now!",
                                    "No, make my data public later"],
                                    index=None
                            )
        if visibility_option == "No, make my data public later":
            today = datetime.now().date()
            next_year = today + timedelta(days=365)
            date_visible = st.date_input("Data will be visible by:", None,
                                             min_value = today,
                                             max_value = next_year)
            if date_visible is not None:
                st.success(f'Data will be visible and public on: {date_visible}.', icon="✅")

        if visibility_option == "Yes, make my data visible now!":
            st.success(" Data is going to be visible and public now.", icon="✅")

        st.write("After submitting your Data, a report with the results will be sent to your e-mail.")
        email = st.text_input('Provide your e-mail address:')
        confirmation = st.checkbox('I am sure that the data uploaded is correct and I want to submit the data.')

        st.session_state.hinderSubmit = (confirmation == False or visibility_option == None or email == "")

        Data_button = st.button("Submit Data",
                                type="primary",
                                disabled=st.session_state.hinderSubmit,
                                use_container_width=True)

        if Data_button and (xls_1 and xls_2):

            os.makedirs(LOCAL_DIRECTORY_TEMPLATES, exist_ok=True)
            os.makedirs(LOCAL_DIRECTORY_YAML, exist_ok=True)

            # Get all the yaml files
            parse_ex_to_yaml(LOCAL_DIRECTORY_YAML, xls_2)

            # Define the yaml files path
            info_file_study = os.path.join(LOCAL_DIRECTORY_YAML, 'STUDY.yaml')
            info_file_experiments = os.path.join(LOCAL_DIRECTORY_YAML, 'EXPERIMENTS.yaml')
            info_compart_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMPARTMENTS.yaml')
            info_mem_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITY_MEMBERS.yaml')
            info_comu_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITIES.yaml')
            info_pert_file = os.path.join(LOCAL_DIRECTORY_YAML, 'PERTURBATIONS.yaml')

            # Do the test to the yaml files according to the sheet
            data_study_yaml = load_yaml(info_file_study)
            errors = test_study_yaml(data_study_yaml)

            data_experiment_yaml = load_yaml(info_file_experiments)
            errors.append(test_experiments_yaml(data_experiment_yaml))

            data_compartment_yaml = load_yaml(info_compart_file)
            errors.append(test_compartments_yaml(data_compartment_yaml))

            data_comu_members_yaml = load_yaml(info_mem_file)
            errors.append(test_comu_members_yaml(data_comu_members_yaml))

            data_comu = load_yaml(info_comu_file)
            errors.append(test_communities_yaml(data_comu))

            data_pertu = load_yaml(info_pert_file)
            errors.append(test_perturbation_yaml(data_pertu))

            # Check that there is no error, otherwise, show error and do not upload data
            st.info(errors)
            if not all(not sublist for sublist in errors):
                for i in errors:
                    st.error(f"Data uploading unsuccessful: {i}. Please correct and try again!")

            # else, populate the db and give the unique ids to the user if not error
            # if errors during the population function then the function stops and the errors are printed
            else:

                study_id, errors, errors_logic, studyUniqueID, projectUniqueID, project_id  = populate_db(measure_tech,
                                                                                                        metabo_col,
                                                                                                        all_taxa ,
                                                                                                        xls_1,
                                                                                                        info_file_study,
                                                                                                        info_file_experiments,
                                                                                                        info_compart_file,
                                                                                                        info_mem_file,
                                                                                                        info_comu_file,
                                                                                                        info_pert_file,
                                                                                                        conn,
                                                                                                        project_name,
                                                                                                        project_description
                                                                                                        )


                if not (errors and errors_logic) and (study_id and studyUniqueID and projectUniqueID and project_id):
                    st.success(f"""Thank you! your study has been successfully uploaded into our database,
                               **Unique Study ID**: {studyUniqueID} and **Study ID**: {study_id},
                               **Unique Project Id**: {projectUniqueID} and **Project ID**: {project_id}""")

                    # create folder to store study data:
                    path = relative_path_to_src + f"/Data/Growth/{study_id}"
                    growth_file = path + f"/Growth_Metabolites.csv"
                    reads_file = path + f"/Sequencing_Reads.csv"
                    # Create the folder
                    os.makedirs(path, exist_ok=True)
                    # this function stores the raw data in 2 .csv files in a study folder
                    save_data_to_csv(growth_file,reads_file,xls_1)

                else:
                    for i in errors:
                        st.error(f"Data uploading unsuccessful: {i}. Please correct and try again!")
                    for i in errors_logic:
                        st.error(f"Data uploading unsuccessful: {i}. Please correct and try again!")


create_private_project_id, unique_study_id_val, project_name, project_description= tab_step1()
keywords, list_taxa_id, all_strain_data, other_taxa_list = tab_step2()
list_growth, list_metabolites, all_taxa =  tab_step3(keywords, list_taxa_id, all_strain_data, create_private_project_id, unique_study_id_val)
xls_1, xls_2 = tab_step4()
tab_step5(xls_1, xls_2,list_growth, list_metabolites, all_taxa, conn, project_name, project_description)
