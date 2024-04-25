import streamlit as st

def do_search(dropdown_options,input_text_fields):

    conn = st.connection('mysql', type='sql')
    if dropdown_options == 'Study Name':
        df_search_studyname = conn.query('SELECT {input_text_fields} from study;', ttl=600)
    # Perform query.
    df_study = conn.query('SELECT * from study;', ttl=600)
    st.dataframe(df_study)

    df_biologicalrep = conn.query('SELECT * from biologicalreplicate;', ttl=600)
    st.dataframe(df_biologicalrep)

    df_technicalrep = conn.query('SELECT * from technicalreplicate;', ttl=600)
    st.dataframe(df_technicalrep)