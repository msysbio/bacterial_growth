import streamlit as st
from streamlit_extras.app_logo import add_logo
from st_pages import show_pages_from_config
from streamlit_extras.badges import badge

# Preload CSS file
@st.cache_resource
def load_css():
    with open("style.css") as css:
        return css.read()

st.set_page_config(page_title="µGrowthDB", page_icon="🔍", layout='wide')

add_logo("figs/logo_sidebar3.png", height=100)


st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)



st.image('figs/logo.png')
st.write('')
st.write('')
st.write('')
st.write('')


st.markdown("![badge](https://img.shields.io/badge/status-under%20development-orange?style=for-the-badge)")

st.subheader("**Welcome to µGrowthDB**")
st.markdown(
    """
    µGrowthDB is a relational database that provides a structure to store different types of microbial growth data. 
    Our main objective is to serve as a comprehensive resource for researchers interested in studying the growth dynamics of microbial species.
    By providing access to growth projects and studies uploaded by other researchers.µ
    """)

st.page_link("pages/Database_Search.py", label=":blue[**Search Growth Studies**]", help="Click on to start a search")
st.markdown(
    """
    Users can search for experimental data collected from microbial growth studies. The search can be filtered by different experimental conditions and characteristicas like
    Project name, Study name, microbial strains, metabolites, culture media and pH.

    All the data at µGrowthDB is publically available for everyone. To further analyze and compare different datasets we offer the feature of downloading several datasets at once.
    """)
st.page_link("pages/Upload_Data.py", label=":blue[**Upload your Microbial Growth Project and Studies]**", help="Click on to start a sharing")
st.markdown(
    """
    At µGrowthDB, we recognize the invaluable contributions of researchers in advancing our understanding of microbial dynamics. Sharing growth data publicly
    plays a crucial role in increasing scientific progress and collaboration within the research community. We allow reasearcher to upload their experimental data by following five steps 
    that allow us to keep an adquate quality control over the data.
    """)
st.page_link("pages/Visualization_Dashboard.py", label=":blue[**Visualize Growth Data:**]", help="Click on to plot data")
st.markdown(
    """
    Users can visualize all the different microbial growth experiments with its corresponding measured techniques in the database, this means plotting accurate growth curves accross different conditions.
    """)
st.write('')
st.write('')

show_pages_from_config()
