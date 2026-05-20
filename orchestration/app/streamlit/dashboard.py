import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime

st.set_page_config(
    page_title='CityReport Admin',
    page_icon='🏙️',
    layout='wide'
)

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://sa:77java&&@localhost:5432/cityreport'
)
engine = create_engine(DATABASE_URL)


def load_data(query):
    with engine.connect() as conn:
        return pd.read_sql_query(text(query), conn)


st.title('🏙️ CityReport — Διαχειριστικός Πίνακας')
st.markdown('---')

col1, col2, col3 = st.columns(3)

total = load_data('SELECT COUNT(*) as cnt FROM tickets WHERE is_deleted = FALSE')
open_tickets = load_data(
    "SELECT COUNT(*) as cnt FROM tickets t "
    "JOIN statuses s ON t.status_id = s.id "
    "WHERE s.name != 'Επιλύθηκε' AND s.name != 'Απορρίφθηκε' "
    "AND t.is_deleted = FALSE"
)
resolved = load_data(
    "SELECT COUNT(*) as cnt FROM tickets t "
    "JOIN statuses s ON t.status_id = s.id "
    "WHERE s.name = 'Επιλύθηκε' AND t.is_deleted = FALSE"
)

col1.metric('Σύνολο Αναφορών', total.iloc[0]['cnt'])
col2.metric('Ανοιχτές Αναφορές', open_tickets.iloc[0]['cnt'])
col3.metric('Επιλυμένες', resolved.iloc[0]['cnt'])

st.markdown('---')

tab1, tab2, tab3 = st.tabs(['📋 Αναφορές', '📊 Στατιστικά', '⚙️ Διαχείριση'])

with tab1:
    st.subheader('Φίλτρα')

    statuses = load_data(
        "SELECT id, name FROM statuses WHERE is_deleted = FALSE ORDER BY id"
    )
    categories = load_data(
        "SELECT id, name FROM categories WHERE is_deleted = FALSE ORDER BY id"
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        status_filter = st.selectbox(
            'Κατάσταση',
            options=['Όλες'] + statuses['name'].tolist()
        )
    with filter_col2:
        category_filter = st.selectbox(
            'Κατηγορία',
            options=['Όλες'] + categories['name'].tolist()
        )
    with filter_col3:
        search = st.text_input('Αναζήτηση', placeholder='Τίτλος ή περιγραφή...')

    query = """
        SELECT
            t.id::text,
            t.title,
            LEFT(t.description, 100) as description,
            c.name as category,
            s.name as status,
            t.latitude,
            t.longitude,
            t.photo_url,
            t.ai_priority_suggestion,
            t.created_at::text as created_at
        FROM tickets t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN statuses s ON t.status_id = s.id
        WHERE t.is_deleted = FALSE
    """
    params = {}

    if status_filter != 'Όλες':
        query += " AND s.name = :status"
        params['status'] = status_filter
    if category_filter != 'Όλες':
        query += " AND c.name = :category"
        params['category'] = category_filter
    if search:
        query += " AND (t.title ILIKE :search OR t.description ILIKE :search)"
        params['search'] = f'%{search}%'

    query += " ORDER BY t.created_at DESC"

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)

    st.dataframe(
        df,
        column_config={
            'id': 'ID',
            'title': 'Τίτλος',
            'description': 'Περιγραφή',
            'category': 'Κατηγορία',
            'status': 'Κατάσταση',
            'ai_priority_suggestion': 'Προτεραιότητα',
            'created_at': 'Ημερομηνία',
            'photo_url': st.column_config.ImageColumn('Φωτογραφία'),
            'latitude': st.column_config.NumberColumn('Latitude', format='%.6f'),
            'longitude': st.column_config.NumberColumn('Longitude', format='%.6f')
        },
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader('Στατιστικά Αναφορών')

    status_counts = load_data(
        "SELECT s.name, COUNT(t.id) as count "
        "FROM statuses s "
        "LEFT JOIN tickets t ON t.status_id = s.id AND t.is_deleted = FALSE "
        "WHERE s.is_deleted = FALSE "
        "GROUP BY s.name"
    )
    fig_status = px.pie(
        status_counts,
        values='count',
        names='name',
        title='Ανά Κατάσταση'
    )
    st.plotly_chart(fig_status, use_container_width=True)

    category_counts = load_data(
        "SELECT c.name, COUNT(t.id) as count "
        "FROM categories c "
        "LEFT JOIN tickets t ON t.category_id = c.id AND t.is_deleted = FALSE "
        "WHERE c.is_deleted = FALSE "
        "GROUP BY c.name"
    )
    fig_cat = px.bar(
        category_counts,
        x='name',
        y='count',
        title='Ανά Κατηγορία',
        labels={'name': 'Κατηγορία', 'count': 'Πλήθος'}
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    priority_counts = load_data(
        "SELECT ai_priority_suggestion, COUNT(*) as count "
        "FROM tickets "
        "WHERE is_deleted = FALSE AND ai_priority_suggestion IS NOT NULL "
        "GROUP BY ai_priority_suggestion"
    )
    if not priority_counts.empty:
        fig_priority = px.bar(
            priority_counts,
            x='ai_priority_suggestion',
            y='count',
            title='Προτεινόμενη Προτεραιότητα (AI)',
            labels={
                'ai_priority_suggestion': 'Προτεραιότητα',
                'count': 'Πλήθος'
            }
        )
        st.plotly_chart(fig_priority, use_container_width=True)

with tab3:
    st.subheader('Ενημέρωση Κατάστασης Αναφοράς')

    tickets_df = load_data(
        "SELECT t.id::text, t.title, s.name as status "
        "FROM tickets t "
        "JOIN statuses s ON t.status_id = s.id "
        "WHERE t.is_deleted = FALSE "
        "ORDER BY t.created_at DESC"
    )

    if not tickets_df.empty:
        selected_id = st.selectbox(
            'Επιλέξτε Αναφορά',
            options=tickets_df['id'].tolist(),
            format_func=lambda x: f"{x[:8]}... - {tickets_df[tickets_df['id'] == x]['title'].values[0]}"
        )

        new_status = st.selectbox(
            'Νέα Κατάσταση',
            options=statuses['name'].tolist()
        )
        admin_notes = st.text_area('Σημειώσεις Διαχειριστή')

        if st.button('Ενημέρωση', type='primary'):
            status_id = statuses[statuses['name'] == new_status]['id'].values[0]
            with engine.connect() as conn:
                conn.execute(
                    text(
                        "UPDATE tickets SET status_id = :sid, admin_notes = :notes, "
                        "updated_at = :now WHERE id::text = :tid"
                    ),
                    {
                        'sid': int(status_id),
                        'notes': admin_notes,
                        'now': datetime.utcnow(),
                        'tid': selected_id
                    }
                )
                conn.commit()
            st.success(f'✅ Η αναφορά {selected_id[:8]}... ενημερώθηκε σε "{new_status}"')
            st.rerun()
