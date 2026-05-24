import pandas as pd
import streamlit as st
from data.repository import TicketRepository

# setup page.
st.set_page_config(page_title="Λεπτομέρειες Συμβάντος", layout="centered")

# init repo.
repo = TicketRepository()

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

st.divider()

with st.container():
    k1, k2 = st.columns(2)
    with k1:
        st.metric("Κατάσταση", ticket.status_name or "—")
    with k2:
        st.metric("Κατηγορία", ticket.category_name or "—")

with st.container():
    t1, t2 = st.columns(2)
    with t1:
        st.metric("Δημιουργήθηκε", ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else "—")
    with t2:
        st.metric("Τελευταία Ενημέρωση", ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else "—")

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