import pandas as pd
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
        st.metric("Μη επιλυμένα Συμβάντα", str(len([t for t in tickets if t.status_id not in (3, 4)])))

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
        "Ημερομηνία": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "-",
        "Προβολή": f"./ticket_detail?ticket_id={t.id}",
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

# map area.
locations = [t for t in tickets if t.latitude is not None and t.longitude is not None]
st.subheader("Χάρτης Συμβάντων")
if locations:
    map_data = [{"lat": float(t.latitude), "lon": float(t.longitude)} for t in locations]
    st.map(pd.DataFrame(map_data), zoom=12)
else:
    st.info("Δεν βρέθηκαν σημεια lat & long για την αποτύπωση του Χάρτη")

st.subheader("Ανάλυση Προτεραιότητας")

urgent = sum(1 for t in tickets if t.ai_priority_suggestion == "⚠️ Επείγον")
normal = sum(1 for t in tickets if t.ai_priority_suggestion == "Κανονική Προτεραιότητα")
unrated = sum(1 for t in tickets if not t.ai_priority_suggestion)

chart_data = pd.DataFrame({
    "Κατάσταση": ["⚠️ Επείγον", "Κανονική Προτεραιότητα", "Χωρίς Αξιολόγηση"],
    "Πλήθος": [urgent, normal, unrated],
})
chart_data = chart_data[chart_data["Πλήθος"] > 0]

if not chart_data.empty:
    st.bar_chart(chart_data, x="Κατάσταση", y="Πλήθος")
else:
    st.info("Δεν βρέθηκαν δεδομένα για την αποτύπωση του γραφήματος.")

st.subheader("Ανάλυση Κατηγοριών")

counts = {}
for t in tickets:
    name = t.category_name or "Χωρίς Κατηγορία"
    counts[name] = counts.get(name, 0) + 1

cat_data = pd.DataFrame(
    sorted(counts.items(), key=lambda x: x[1], reverse=True),
    columns=["Κατηγορία", "Πλήθος"],
)

if not cat_data.empty:
    st.bar_chart(cat_data, x="Κατηγορία", y="Πλήθος")
else:
    st.info("Δεν βρέθηκαν δεδομένα για την αποτύπωση του γραφήματος.")

st.subheader("Συμβάντα ανά Ημέρα")

tickets_over_time = pd.DataFrame(
    [{"Ημερομηνία": t.created_at.date(), "Πλήθος": 1} for t in tickets if t.created_at]
)

if not tickets_over_time.empty:
    tickets_over_time = tickets_over_time.groupby("Ημερομηνία").sum().reset_index()
    tickets_over_time = tickets_over_time.set_index("Ημερομηνία")
    st.line_chart(tickets_over_time, y="Πλήθος")
else:
    st.info("Δεν βρέθηκαν δεδομένα για την αποτύπωση του γραφήματος.")

st.subheader("Κατανομή Καταστάσεων")

counts = {}
for t in tickets:
    name = t.status_name or "Χωρίς Κατάσταση"
    counts[name] = counts.get(name, 0) + 1

status_data = pd.DataFrame(
    sorted(counts.items(), key=lambda x: x[1], reverse=True),
    columns=["Κατάσταση", "Πλήθος"],
)

if not status_data.empty:
    st.bar_chart(status_data, x="Κατάσταση", y="Πλήθος")
else:
    st.info("Δεν βρέθηκαν δεδομένα για την αποτύπωση του γραφήματος.")

st.subheader("Κατηγορία vs Προτεραιότητα")

rows = []
for t in tickets:
    cat = t.category_name or "Χωρίς Κατηγορία"
    pri = t.ai_priority_suggestion or "Χωρίς Αξιολόγηση"
    rows.append({"Κατηγορία": cat, "Προτεραιότητα": pri})

if rows:
    cross_data = pd.DataFrame(rows).groupby(["Κατηγορία", "Προτεραιότητα"]).size().unstack(fill_value=0)
    st.bar_chart(cross_data, stack=True)
else:
    st.info("Δεν βρέθηκαν δεδομένα για την αποτύπωση του γραφήματος.")

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