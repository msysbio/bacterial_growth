import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
import numpy as np
from create_excel import create_excel_fun
from datetime import datetime, timedelta
from io import StringIO
import time
from df_parse_ex import parse_excel
from constants import LOCAL_DIRECTORY
from create_rawdata_excel import create_rawdata_excel_fun
import json
from streamlit_tags import st_tags




st.set_page_config(page_title="Upload Data", page_icon="📤", layout='wide')

add_logo("logo_sidebar2.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.image('pages/UploadBanner.png')

global unique_community_ids
global list_selected_microbes
global list_strains
list_strains = []
list_selected_microbes = []
strain_data = {}
strain_data1 = {}
data_excel = None

unique_community_ids = set()

if 'rows_communities' not in st.session_state:
    st.session_state['rows_communities'] = 0

def increase_rows():
    st.session_state['rows_communities'] += 1

def decrease_rows():
    st.session_state['rows_communities'] -= 1

@st.cache_data
def connection_df_taxonomy(input_other_taxa):
    conn = st.connection('mysql', type='sql')
    tax_other_query = f"SELECT * FROM taxa WHERE tax_names LIKE '%{input_other_taxa}%';"
    df_other_taxonomy = conn.query(tax_other_query, ttl=600)
    return df_other_taxonomy



def display_strain_row(index):
    strain_data = {}
    with st.container():
        col1_add, col2_add = st.columns(2)
        # Add a text input field to the first column
        with col1_add:
            other_name = st.text_input('*Name of the microbial strian:', placeholder='1. Provide a name to the microbial strain',help='Complete with the name of your microbial strain', key=f'other_name{index}')
            strain_data[f'name_{index}'] = other_name
        with col2_add:
            other_description = st.text_input('*Description of the microbial strian:', placeholder='2. Provide an informative desciption of the microbial strain',help='Complete with a description of your microbial strain', key=f'other_description{index}')
            strain_data[f'description_{index}'] = other_description
        col3_add, col4_add, col5_add, col6_add= st.columns([0.39,0.39,0.12,0.10])
        with col3_add:
            input_other_taxa = st.text_input('*Search microbial strain species:',placeholder='3. Search microbial strain species',help='Type the specific microbial strain  species, then press enter', key=f'input_other_taxa{index}')
        with col4_add:
            df_other_taxonomy = connection_df_taxonomy(input_other_taxa)
            df_taxa_other_name = df_other_taxonomy['tax_names']
            other_taxonomy = st.selectbox('*Select microbial strain species', options=df_taxa_other_name,index=None,placeholder="4. Select one of the species below",help='Select only one microbial strain species, then click on add',key=f'other_taxonomy{index}')
            strain_data[f'taxa_{index}'] = other_taxonomy
        with col5_add:
            st.write("")
            st.write("")
            st.button('Add More',key=f'add_button_{index}', type='primary',on_click=increase_rows)

        with col6_add:
            st.write("")
            st.write("")
            st.button('Delete',key=f'delete_button_{index}',type='primary', on_click=decrease_rows)
    return strain_data




st.markdown(
    """
    Thank you for choosing to share your Bacterial Growth data with us. Your commitment to sharing study and experimental data is essential 
    for advancing our understanding of gut microbiome dynamics. Your contribution plays a vital role in driving research forward and enhancing 
    our collective knowledge in this field.

    To successfully submit your data, please ensure that you follow the instructions provided in each of the following steps. Adhering to these 
    instructions helps us maintain the quality of our database and ensures the accuracy and reliability of the information stored within it. 
    Thank you for your cooperation in maintaining data integrity and reliability.
""")

st.write('')
st.write('')


# Step 1
tab1, tab21,  tab2, tab3, tab4, tab5, tab6 = st.tabs(["Step 1", "Step 2","Step 3", "Step 4", "Step 5", "Step 6","Step 7"])
css = '''
<style>
.stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:1.6rem;
    font-weight: bold;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)

if 'verify' not in st.session_state:
    st.session_state['verify'] = 0

def update_verify():
    st.session_state['verify'] = 1

def create_StudyID():
    st.success("Your Study ID is 123456789, copy this number somewhere safe since you will need to upload new versions in the future")
    st.info("Now go to Step 2 and folow the instructions")


def tab_step1():
    with tab1:
        st.subheader("1. Select type of data submission")
        st.markdown(
            """
            **Data Submission Options:**
            - [x] **Add a new study to a new project:** Choose this option if you're uploding study data from a new, non existing project.
            - [x] **Add a new study to a previos project:** Choose this option if you're updating a new study to an already existing project.
            - [x] **Add a new version of a study to a previous project:** Choose this option if you're updating a new study version to an already existing project.
            
            **Unique study ID:** Please provide the unique study ID of the previous study you wish to update. This ensures continuity and helps us maintain the database up to data.
            
            **Unique project ID:** Please provide the unique project ID of the existing project where you wish to add a new study or update a previous created study.

            If you do not remember the unique IDs please follow the intructions in (link).
            """)

        options = ['Add a new study to a new project','Add a new study to a previos project','Add a new version of a study to a previous project']
        new_ckeck = st.selectbox('Select the type of data submission:', options, None, 
                                 help= 'Choose one of the options for your data submission.')

        if new_ckeck == 'Add a new study to a new project':
            col1, col2 = st.columns([0.87,0.13])
            with col1:
                project_name = st.text_input('Project name:',help='Name the new project',placeholder='1. Provide a name for your new project')
                project_description = st.text_input('Project description:',help='Description the new project',placeholder='2. Provide a project description')
            with col2:
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                create_button = st.button("Create project",type="primary")
            if create_button and project_name and project_description:
                update_verify()
                st.info(f"Your New proyect **{project_name}** was successfully created! Your unique proyect ID is **1234**, Go to **Step 2** and folow the instructions!", icon="✅")
                # then verify that the number is correct
        if new_ckeck == 'Add a new study to a previos project':
            col1, col2 = st.columns([0.85,0.15])
            with col1:
                project_id = st.text_input('Project unique ID:',help='Provide the unique ID of the project you want to add a new study',placeholder='1. Provide the unique project ID')
            with col2:
                st.write('')
                st.write('')
                verify_button = st.button("Verify unique ID",type="primary")
            if verify_button:
                update_verify()
                st.info("Go to **Step 2** and folow the instructions!", icon="✅")

        if new_ckeck == 'Add a new version of a study to a previous project':
            col1, col2 = st.columns([0.8,0.2])
            with col1:
                project_id = st.text_input('Project unique ID:',help='Provide the unique ID of the study project you want to add a new version',placeholder='1. Provide the unique project ID')
                study_id = st.text_input('Study unique ID:',help='Provide the unique ID of the study you want to add a new version',placeholder='2. Provide the unique study ID')
            with col2:
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                verify2_button = st.button("Verify unique IDs",type="primary")
            if verify2_button:
                update_verify()
                st.info("Go to **Step 2** and folow the instructions!", icon="✅")
            #generate_button = st.button("Create Study ID",type="primary",use_container_width = True)
            #if generate_button:
            #    create_StudyID()
            #    update_verify().
        
        
def tab_step2_1():
    keywords = []
    all_strain_data = []
    list_taxa_id = []
    other_taxa_list = []
    all_taxa_list = []
    strain_data1 = {}
    if 'list_strains' not in st.session_state:
        st.session_state['list_strains'] = []

    if st.session_state.get('add'):
        val_taxonomy = st.session_state.get('select_taxa')
        if val_taxonomy:
            st.session_state.list_strains.append(val_taxonomy)
        st.session_state['input_taxa'] = ''
        st.session_state['select_taxa'] = None
    

    with tab21:
        st.subheader("2. Select all the microbial strains used in the study")
        st.markdown(
            """
            Using the search tap bellow, select all the microbial strains used in your study as well as any uncultured communities, click on 'add' to include the selected option. 
            Once you are sure all the different community members are defined, click on 'save'.
            """)
        col1, col2, col3 = st.columns([0.45,0.45,0.1])
        with col1:

            input_taxa = st.text_input('Search microbial strain:', key = 'input_taxa',placeholder='1. Search microbial strain',help='Type the specific microbial strain, then press enter')
        with col2:
            df_taxonomy = connection_df_taxonomy(input_taxa)
            df_taxa_name = df_taxonomy['tax_names']
            taxonomy = st.selectbox('Select microbial strain', options=df_taxa_name,index=None,placeholder="2. Select one of the strains below",key = 'select_taxa',help='Select only one microbial strain, then click on add')
            val_taxonomy = taxonomy
        with  col3:
            st.write("")
            st.write("")
            add_button = st.button('Add',key='add',type='primary')

        
        keywords = st.multiselect(label='Microbial species added', options=st.session_state.list_strains,default = st.session_state.list_strains)
        to_remove = [k for k in st.session_state.list_strains if k not in keywords]
        list_taxa_id = [df_taxonomy[df_taxonomy['tax_names'] == keyword].iloc[0]['tax_id'] for keyword in keywords]
        for k in to_remove:
            st.session_state.list_strains.remove(k)
        for i in keywords:
            strains_df = df_taxonomy[df_taxonomy['tax_names'] == i]
            taxa_id = strains_df.iloc[0]['tax_id']
            st.info(f'For more information about **{i}** go to the NCBI Taxonomy ID:[{taxa_id}](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={taxa_id})', icon="❕")
        
        
        other_strains=st.radio("*Did you find all the microbial strains?:",
                                       ["Yes, all microbial strains used in my study have been added.",
                                        "No, Some microbial strains were not found"],
                                        index=None)
        

        if other_strains == "Yes, all microbial strains used in my study have been added.":
            list_taxa_id = [df_taxonomy[df_taxonomy['tax_names'] == keyword].iloc[0]['tax_id'] for keyword in keywords]
            st.success("Done! Microbial strains saved, then go to **Step 3**", icon="✅")

        

        if other_strains == "No, Some microbial strains were not found":
            with st.container():
                col6, col7 = st.columns([0.5,0.5])
                with col6:
                    other_name = st.text_input('*Name of the microbial strian:', placeholder='1. Provide a name to the microbial strain',help='Complete with the name of your microbial strain')
                    strain_data1['name_0'] = other_name
                with col7:
                    other_description = st.text_input('*Description of the microbial strian:', placeholder='2. Provide an informative desciption of the microbial strain',help='Complete with a description of your microbial strain')
                    strain_data1['description_0'] = other_description
                col8, col9, col10 = st.columns([0.44,0.44,0.12])
                with col8:
                    input_other_taxa = st.text_input('*Search microbial strain species:',placeholder='3. Search microbial strain species',help='Type the specific microbial strain  species, then press enter')
                with col9:
                    df_other_taxonomy = connection_df_taxonomy(input_other_taxa)
                    df_taxa_other_name = df_other_taxonomy['tax_names']
                    other_taxonomy = st.selectbox('*Select microbial strain species', options=df_taxa_other_name,index=None,placeholder="4. Select one of the species below",help='Select only one microbial strain species, then click on add')
                    strain_data1['taxa_0'] = other_taxonomy
                if other_taxonomy:
                    strains_df = df_taxonomy[df_taxonomy['tax_names'] == other_taxonomy]
                    taxa_id = strains_df.iloc[0]['tax_id']
                    st.info(f'For more information about **{other_taxonomy}** go to the NCBI Taxonomy ID:[{taxa_id}](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={taxa_id})', icon="❕")
                    other_taxa_list.append(taxa_id)
                    
                with  col10:
                    st.write("")
                    st.write("")
                    add_other_button = st.button('Add More',key='add_other',type='primary',on_click=increase_rows)

            for i in range(st.session_state['rows_communities']):
                st.write('')
                st.write('')
                strain_data = display_strain_row(i+1)
                all_strain_data.append(strain_data)
                name = strain_data[f'taxa_{i+1}']
                strains_df = df_taxonomy[df_taxonomy['tax_names'] == strain_data[f'taxa_{i+1}']]
                taxa_id = strains_df.iloc[0]['tax_id']
                st.info(f'For more information about **{name}** go to the NCBI Taxonomy ID:[{taxa_id}](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id={taxa_id})', icon="❕")
            
            save_all = st.button('Save All',type='primary')
            if save_all:
                list_taxa_id = [df_taxonomy[df_taxonomy['tax_names'] == keyword].iloc[0]['tax_id'] for keyword in keywords]
                all_strain_data.append(strain_data1)
                print(all_strain_data)
                for i in range(st.session_state['rows_communities']):
                    name = strain_data[f'taxa_{i+1}']
                    strains_df = df_taxonomy[df_taxonomy['tax_names'] == strain_data[f'taxa_{i+1}']]
                    taxa_id = strains_df.iloc[0]['tax_id']
                    other_taxa_list.append(taxa_id)
                st.success("Done! Microbial strains saved, then go to **Step 3**", icon="✅")

    return keywords,list_taxa_id ,all_strain_data, other_taxa_list


        


def tab_step2(keywords, list_taxa_id,all_strain_data,other_taxa_list):
   
    with tab2:
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
                colu11, colu22 = st.columns(2)
                number_vessels = 0
                number_columns = 0
                number_rows = 0
                with colu11:
                    type_vessel = st.selectbox('*Select the type of vessels used:', ['Bottles', 'Agar-plates', 'Well-plates', 'mini-bioreactors'],index=None,help='Choose which type of vessel was used in your study')
                with colu22:
                    if type_vessel == 'Bottles' or type_vessel == 'Agar-plates':
                        number_vessels = st.text_input('*Number of bottles/agar-plates:',help='Please specify the total number of individual bottle or agar-plates in your study.',value=0)
                    else:
                        number_columns = st.text_input('*Number of columns:',help='Please specify the number of columns in the well-plate or mini-bioreactor utilized in your study.',value=0)
                        number_rows = st.text_input('*Number of rows:', help='Please specify the number of rows in the well-plate or mini-bioreactor utilized in your study.',value=0)

                number_timepoints = st.text_input('*Number of measurement time-points:', help='Please provide the number of measurement time-points per experiment. If different time-points were used across experiments, please specify the largest one.')
                measure_tech = st.multiselect('*Select the techniques used to measure growth:',['Optical Density (OD)', 'Plate-Counts', 'Flow Cytometry (FC)', '16S rRNA-seq'],help='Select all the measurement techniques used in your study to quantify bacterial growth.')
                conn = st.connection('mysql', type='sql')
                df_metabolites = conn.query('SELECT * from metabolites;', ttl=600)
                df_metabo_name = df_metabolites['metabo_name']
                meta_col = st.multiselect('If metabolites were measure, select which ones:',df_metabo_name,help='Select all the metabolites quantified in your study, please make sure to use the correct name.')  


                if meta_col:
                    for i in meta_col:
                        filtered_df = df_metabolites[df_metabolites['metabo_name'] == i]
                        cheb_id = filtered_df.iloc[0]['cheb_id']
                        st.info(f'For more information about **{i}** go to [{cheb_id}](https://www.ebi.ac.uk/chebi/searchId.do?chebiId={cheb_id})', icon="❕")


                excel_rawdata = create_rawdata_excel_fun(measure_tech, meta_col,type_vessel,number_vessels,number_columns,number_rows,number_timepoints,keywords)
                disabled = not measure_tech

                st.text('')
                st.text('')
                down_button = st.download_button(label='Click here to Download the Data Template',
                                    data=excel_rawdata,
                                    file_name='template_raw_data.xlsx',
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
                    - **STUDY:** In this sheet you will have to complete the basic information of the Study you are about to upload. A Study is always part of a Project so you will have to provide the corresponding **project unique ID**.
                    - **EXPERIMENTS** In this sheet you will complete all the details of your study. Each row represent an **Experiment** and each column specific information about it. Fill as many rows as many different experiments you have in your study. **ORANGE COLUMNS** are present in other sheets and should be completed with the same values.
                    - **COMPARTMENTS:** Details of the different compartments used for the experiments. If identical conditions across different experiments occur, these should be considered as a single compartment. So complete as many rows as different conditions setups you have among the experiments in your study (**EXPERIMENTS** rows).
                    - **COMMUNITY_MEMBERS:** Information with respect to the various strains used in this study. Each row in this tab corresponds to a strain that has been part of at least one experiment.
                    - **COMMUNITIES:** Definition of the microbial **COMMUNITIES** using the **Member_ID** auto-completed in **COMMUNITY_MEMBERS** sheet. Each row represents a different community. These **COMMUNITIES** are then used in the **EXPERIMENTS** sheet to describe the community used per experiment in each compartment. 
                    - **PERTURBATIONS:** In this sheet you will fill all the information related to the different perturbations made to an experiment (**Experiment_ID**). There are two types of perturbations possible: when altering compartment conditions such as: pH, temperature etc. or when adding new microbial **COMMUNITIES** like: environmental samples or new microvial strains. 
                    Complete each section carefully according to the instructions. **DO NOT** modify the file by adding or deleating columns. 
                    """)
                excel_data = create_excel_fun(keywords, list_taxa_id,all_strain_data,other_taxa_list)
                
                down_study_button = st.download_button(label='Click here to Download the Study Template',
                                    data=excel_data,
                                    file_name='example.xlsx',
                                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                    type="primary",
                                    use_container_width = True,
                                    )
                if down_study_button:
                    with st.spinner('Downloading file'):
                        time.sleep(2)
                        st.success("Done! Complete file, then go to **Step 3**", icon="✅")

        else:
            st.warning("Go back to Step 1 and fill in the details!", icon="⚠️")


def tap_step3():
    
    bact_mod = 0
    df_filtered_bact = 0
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("1. Upload Data Template")
            st.markdown(
            """
            Upload below the Excel Data file once completed with all the data measured in your 
            study according to the instructions provided in the **Step 2**. Remember that no modifications are allowed after 
            you submit the data. Please double check below that all the celds are correct.
            """)  
            uploaded_file = st.file_uploader("Upload data file .xlsx here:",help='Only one .xlsx file allowed')

            if uploaded_file is not None:
                # Read the Excel file
                xls = pd.ExcelFile(uploaded_file)
                # Get sheet names
                sheet_names = xls.sheet_names
                # Display sheet selection dropdown
                selected_sheet = st.selectbox("Select the Excel sheet you want to visualize", sheet_names)
                # Read the selected sheet
                df = pd.read_excel(xls, engine='openpyxl', sheet_name=selected_sheet)
                
                # Display the DataFrame
                st.dataframe(df)
        with col2:
            st.subheader("2. Upload Study Template")
            st.markdown(
            """
            Upload below the Excel Data file once completed with all the data measured in your 
            study according to the instructions provided in the **Step 2**. Remember that no modifications are allowed after 
            you submit the data. Please double check below that all the celds are correct.
            """)  
            uploaded_file_2 = st.file_uploader("Upload study file .xlsx here:",help='Only one .xlsx file allowed')

            if uploaded_file_2 is not None:
                # Read the Excel file
                xls = pd.ExcelFile(uploaded_file_2)
                # Get sheet names
                sheet_names = xls.sheet_names
                # Display sheet selection dropdown
                selected_sheet_2 = st.selectbox("Select the Excel sheet you want to visualize", sheet_names, key='box_2')
                
                # Read the selected sheet
                df_2 = pd.read_excel(xls, engine='openpyxl', sheet_name=selected_sheet_2)
                
                # Display the DataFrame
                st.dataframe(df_2)

                df_study_data = pd.read_excel(xls, engine='openpyxl', sheet_name='STUDY_DATA')
                global unique_community_ids
                unique_community_ids = set()
                for ids in df_study_data['Comunity_ID']:
                    if ',' in ids:
                        unique_community_ids.update(id.strip() for id in ids.split(','))
                    else:
                        unique_community_ids.add(ids.strip())


        st.warning(" Verify that all the data and study information are correct! No modifications to the data after uploaded are allowed.", icon="⚠️")
        st.info("After checking that all the data provided is correct, click on **Save uploaded files**.")
        submit_button = st.button("Save uploaded files",type="primary",use_container_width = True)
        if submit_button:
            st.success("Done! Now go to **Step 4** and fill in the details.", icon="✅")

        

def tap_step5():
    with tab5:
        st.subheader("Define the mutations done in the microbial strains")
        st.markdown(
            """
            If in your study any of the bacterial strains used were genetically modified or bio-egineered, please select the mutation done on the specific strain.
            If the specific mutation is not within the options select: **Other**. If the microbial strains were not mutated select **None**.
            """) 

        if list_selected_microbes:
            for i in list_selected_microbes:
                if i != 'Bacteria':
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f'{i}')
                    with col2:
                        mutation_options = st.selectbox("Select Mutation options:", ['None', 'Other', 'Mutation1'],key = f'mutation_ops{i}')
                        if mutation_options == 'Other':
                            st.text_input("New mutation:", key=f'mutation_other{i}')
            
            mutations_button = st.button('Save Mutations',type="primary",use_container_width = True)
            if mutations_button:
                    st.success("Done! Now go to **Step 6** and fill in the details.", icon="✅")
        




def tap_step6():
    with tab6:
        st.write("# 🔧 Data visibility")
        st.write("By default your data will be visible and public in the database. Do you want to make your data visible now?")
        visibility_option=st.radio("Visibility options:",
                                       ["Yes, make my data visible now!",
                                        "No, make my data public later"],
                                        index=None)
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
        Data_button = st.button("Submit Data",type="primary",use_container_width = True)




tab_step1()
keywords,list_taxa_id,all_strain_data,other_taxa_list = tab_step2_1()
tab_step2(keywords, list_taxa_id,all_strain_data,other_taxa_list)
tap_step3()
tap_step5()
tap_step6()
