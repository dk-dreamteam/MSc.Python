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

with st.container():
    k1, k2 = st.columns(2)
    with k1:
        st.metric("Κατάσταση", ticket.status_name or "—")
    with k2:
        st.metric("Κατηγορία", ticket.category_name or "—")

st.metric("Δημιουργήθηκε", ticket.created_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.created_at else "—")

st.divider()

# photo area.
if ticket.photo_url:
    st.image(ticket.photo_url, caption="Φωτογραφία συμβάντος")
else:
    st.info("Δεν καταχωρήθηκε φωτογραφία")

st.divider()

# map area.
st.metric("Διεύθυνση", ticket.address or "—")

lat = f"{ticket.latitude:.6f}" if ticket.latitude is not None else "—"
lon = f"{ticket.longitude:.6f}" if ticket.longitude is not None else "—"
st.metric("Συντεταγμένες", f"{lat}, {lon}")

if ticket.ai_priority_suggestion:
    cols = st.columns([1, 3])
    with cols[0]:
        st.markdown("**AI Πρόταση Προτεραιότητας**")
    with cols[1]:
        st.markdown(ticket.ai_priority_suggestion)

if ticket.admin_notes:
    st.markdown("**Σημειώσεις Διαχειριστή**")
    st.write(ticket.admin_notes)

cols = st.columns([1, 3])
with cols[0]:
    st.markdown("**Ενημερώθηκε**")
with cols[1]:
    st.caption(ticket.updated_at.strftime("%Y-%m-%d %H:%M:%S") if ticket.updated_at else "-")
