import streamlit as st

# init services
from data.repository import TicketRepository
repo = TicketRepository()

# configuring page
st.set_page_config(page_title="CityReport", layout="centered")

# title area
st.title("CityReport")
st.write("Καλως ήρθατε στην πλατφόρμα CityReport!")

st.divider()

# overview area
st.header("Επισκόπηση")

with st.container(horizontal=True, gap="medium"):
    cols = st.columns(2, gap="medium")
    with cols[0]:
        st.metric("Σύνολο Συμβάντων", "3")
    with cols[1]:
        st.metric("Μη επιλυμένα Συμβάντα", "1")

st.divider()

# footer area
st.markdown(
    """
    <div style="opacity: 0.6;">
        Made with ❤️ by Dimitris Grevenos me25052 & Konstantinos Kritikakis me25067
    </div>
    """,
    unsafe_allow_html=True,
)  