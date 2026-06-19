# CityReport — MSc.Python

Microservices Αρχιτεκτονική για το σύστημα (CityReport). Υλοποιημένο με Flask, PostgreSQL, Streamlit, Azure Storage (Azurite).

## Προαπαιτούμενα

- [Docker](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.12+

## Εγκατάσταση

```bash
# 1. Clone the repository
git clone <repo-url>
cd MSc.Python

# 2. Start all services (PostgreSQL, Azurite, API, preprocessor, notification, Streamlit)
cd orchestration
docker compose up -d

# 3. Wait for all services to be healthy (30-60s on first run)
docker compose ps

# 4. Populate with sample tickets
cd ..
python create_tickets.py
```

## Services - Containers

| Υπηρεσία | URL | Περιγραφή |
|---|---|---|
| REST API | `http://localhost:5680` | CRUD REST API endpoints για αναφορές |
| Streamlit UI | `http://localhost:5682` | UI Διαχειριστή & λεπτομέρειες συμβάντος |
| Adminer | `http://localhost:8080` | Web διαχείριση PostgreSQL |
| Azurite Blob | `localhost:10000` |  Azure Blob Storage Emulator |
| Azurite Queue | `localhost:10001` | Azure Queue Storage Emulator  |


## Βάση Δεδομένων

Η βάση δεδομένων αρχικοποιείται αυτόματα κατά την πρώτη εκκίνηση μέσω SQL scripts στο `orchestration/scripts/`:

| Script | Σκοπός |
|---|---|
| `1_create_tables.sql` | Δημιουργεί τους πίνακες `tickets`, `categories`, `statuses` |
| `2_create_indexes.sql` | Δημιουργεί indexes |
| `3_seed_init_data.sql` | Εισάγει 7 κατηγορίες και 4 καταστάσεις |

## API Endpoints

| Μέθοδος | Διαδρομή | Περιγραφή |
|---|---|---|
| `POST` | `/tickets` | Δημιουργία αναφοράς (JSON ή multipart με φωτογραφία) |
| `GET` | `/tickets` | Λίστα συμβάντων (προαιρετικά `?status_id=` & `?category_id=`) |
| `GET` | `/tickets/<uuid>` | Λήψη μεμονωμένου αναφοράς |
| `PUT` | `/tickets/<uuid>` | Ενημέρωση αναφοράς |
| `GET` | `/tickets/<uuid>/photo?blob=` | Λήψη φωτογραφίας αναφοράς |
| `GET` | `/statuses` | Λίστα όλων των καταστάσεων |

## Εισαγωγή Αρχικών Δεδομένων

Δύο scripts δημιουργούν δείγματα συμβάντων με φωτογραφίες από το `init_photos/`:

```bash
python create_tickets.py
```

## Τεχνολογίες

- **API:** Flask 3, Flasgger (Swagger)
- **Βάση Δεδομένων:** PostgreSQL 17 (μέσω psycopg2)
- **Ουρά & Blob:** Azure Storage Queues & Blobs (Azurite emulator)
- **Frontend:** Streamlit
- **LLM:** Groq API (συμβατό με OpenAI)
- **Γεωκωδικοποίηση:** OpenStreetMap Nominatim
- **Ειδοποιήσεις:** ntfy.sh
