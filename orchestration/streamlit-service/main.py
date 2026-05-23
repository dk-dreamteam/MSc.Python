import streamlit as st

# init services
from data.repository import TicketRepository
repo = TicketRepository()
tickets = repo.list_tickets()

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
        st.metric("Σύνολο Συμβάντων", str(len(tickets)))
    with cols[1]:
        st.metric("Μη επιλυμένα Συμβάντα", str(len([t for t in tickets if t.status_id != 1])))

st.divider()

# grid area
st.header("Συμβάντα")

# get distinct all the statues from the tickets and create filter bar.
statuses = sorted(set(t.status_name for t in tickets if t.status_name))
selected_statuses = st.multiselect(
    "Φίλτρο κατάστασης",
    options=statuses,
    default=statuses,
)

filtered = [t for t in tickets if t.status_name in selected_statuses]

# apply the filter to the data.
data = [
    {
        "Τίτλος": t.title,
        "Κατάσταση": t.status_name,
        "Κατηγορία": t.category_name or "*Δεν έχει αξιολογηθεί*",
        "Ημερομηνία": t.created_at,
        "Προβολή": f"?ticket_id={t.id}",
    }
    for t in filtered
]

#show the tickets grid.
st.dataframe(
    data,
    column_config={
        "Προβολή": st.column_config.LinkColumn(
            "Προβολή",
            display_text="🔍",
        ),
    },
    use_container_width=True,
    hide_index=True,
)

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