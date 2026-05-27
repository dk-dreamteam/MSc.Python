import os
import pandas as pd
import streamlit as st
from data.repository import TicketRepository
from queue_sender_service import QueueSenderService

# setup page.
st.set_page_config(page_title="Λεπτομέρειες Συμβάντος", layout="centered")

# init repo.
repo = TicketRepository()
queue_sender = QueueSenderService()

TOPIC_NAME = os.getenv("TOPIC_NAME")
if not TOPIC_NAME:
    raise ValueError("TOPIC_NAME must be set")

# get the ticket id from query param.
ticket_id = st.query_params.get("ticket_id")

# if not provided show error.
if not ticket_id:
    st.warning("Δεν επιλέχθηκε συμβάν")
    st.stop()

ticket = repo.get_ticket(ticket_id)

# if not found show error.
if not ticket:
    st.error("Το συμβάν δεν βρέθηκε")
    st.stop()

# start rendering page.
st.header(ticket.title)

st.markdown(f'"{ticket.description}"' if ticket.description else "*Δεν έχει Περιγραφή*")

st.divider()

# my notes area.
st.subheader("Σημειώσεις Διαχειριστή")

notes = st.text_area(
    "Σημειώσεις",
    value=ticket.admin_notes or "",
    placeholder="Προσθέστε σημειώσεις...",
    label_visibility="collapsed",
)

if st.button("Ενημέρωση Σημειώσεων"):
    repo.update_ticket_notes(ticket_id, notes)
    st.toast("Οι σημειώσεις ενημερώθηκαν επιτυχώς!", icon="✅")
    # st.rerun()

# current status area.
st.subheader("Κατάσταση")

# set the statues that correspond to the db.
STATUSES = {
    "Δημιουργήθηκε": 1,
    "Σε Εξέλιξη": 2,
    "Επιλύθηκε": 3,
    "Απορρίφθηκε": 4,
}

status_options = list(STATUSES.keys())

# find the select by the value and get the index to select in the dropdown.
current_idx = status_options.index(ticket.status_name) if ticket.status_name in STATUSES else 0

def on_status_change():
    new_status = st.session_state.status_select
    new_id = STATUSES[new_status]
    repo.update_ticket_status(ticket_id, new_id)
    if new_id == 3:
        queue_sender.send_notification(
            topic_name=TOPIC_NAME,
            title=f"✅ Το συμβάν '{ticket.title}' επιλύθηκε",
            payload=f"Το συμβάν '{ticket.title}' έχει επισημανθεί ως επιλυμένο.",
            click_url=f"http://localhost:5683/ticket_detail?ticket_id={ticket_id}",
        )
    elif new_id == 4:
        queue_sender.send_notification(
            topic_name=TOPIC_NAME,
            title=f"❌ Το συμβάν '{ticket.title}' απορρίφθηκε",
            payload=f"Το συμβάν '{ticket.title}' απορρίφθηκε και δεν θα ληφθεί περαιτέρω ενέργεια.",
            click_url=f"http://localhost:5683/ticket_detail?ticket_id={ticket_id}",
        )
    st.toast(f"Η κατάσταση ενημερώθηκε σε: {new_status}", icon="✅")

st.selectbox(
    "Επιλέξτε κατάσταση",
    options=status_options,
    index=current_idx,
    key="status_select",
    on_change=on_status_change,
    label_visibility="collapsed",
)

with st.container():
    t1, t2 = st.columns(2)
    with t1:
        st.metric("Δημιουργήθηκε", ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else "—")
    with t2:
        st.metric("Τελευταία Ενημέρωση", ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else "—")

st.metric("Κατηγορία", ticket.category_name or "—")

st.divider()

# photo area.
if ticket.photo_url:
    st.image(ticket.photo_url, caption="Φωτογραφία συμβάντος")
else:
    st.info("Δεν καταχωρήθηκε φωτογραφία")

st.divider()

# map area.
st.metric("Διεύθυνση", ticket.address or "—")

# lat = f"{ticket.latitude:.6f}" if ticket.latitude is not None else "—"
# lon = f"{ticket.longitude:.6f}" if ticket.longitude is not None else "—"
# st.metric("Συντεταγμένες", f"{lat}, {lon}")

# show map with pin if the lat and long are not null. Else show empty map.
if ticket.latitude is not None and ticket.longitude is not None:
    df = pd.DataFrame({"lat": [float(ticket.latitude)], "lon": [float(ticket.longitude)]})
    st.map(df, zoom=14)
else:
    st.info("Αναμένεται ο υπολογισμός των συντεταγμένων")
    st.map()

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