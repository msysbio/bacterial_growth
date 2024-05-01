import streamlit as st
from streamlit_extras.app_logo import add_logo
from streamlit_extras.badges import badge

st.set_page_config(page_title="About Us", page_icon="📤", layout='wide')

add_logo("figs/logo_sidebar2.png", height=100)
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.image('figs/AboutUsBanner.png')
st.header('Lab of Micriobial Systems Biology')
st.markdown('<div style="text-align: justify;">We study the structure and dynamics of microbial communities with systems biology methods. Our main interest is to explore microbial community structure and dynamics in silico and in vitro. We therefore work at the boundary of microbial ecology, systems biology and bioinformatics.</div>', unsafe_allow_html=True)
st.text('')
st.text('')

con1 , con2 =  st.columns([0.4, 0.6])
with con1:
    st.subheader('Address')
    st.markdown('''
    Laboratory of Molecular Bacteriology\\
    Department of Microbiology, Immunology and Transplantation (Rega Institute)\\
    KU Leuven\\
    Rega institute, 7th floor (Room 7.B142)\\
    Bus: 1028\\
    Campus Gasthuisberg\\
    Herestraat 49\\
    3000 Leuven\\
    Belgium
    ''')
    st.subheader('More')
    st.page_link("http://www.msysbiology.com/index.html",label= f':blue[**Go to our Website**]')
    badge(type="github", name="msysbio")

iframe_code = '''
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d40278.006351395336!2d4.634398779101553!3d50.87976210000002!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47c160df3fa2d3f3%3A0x8e85c1ed71c08d2d!2sREGA%20INSTITUTE%20KU%20LEUVEN!5e0!3m2!1sen!2sus!4v1712232819219!5m2!1sen!2sus" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
'''

with con2:
    st.markdown(iframe_code, unsafe_allow_html=True)
