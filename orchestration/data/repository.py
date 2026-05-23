import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from data.models import Ticket

logger = logging.getLogger(__name__)


class TicketRepository:
    def __init__(self):
        self.conn_params = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT")),
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
        }
        # Check for missing env vars
        missing = [k for k, v in self.conn_params.items() if v is None]
        if missing:
            raise ValueError(f"Missing DB env vars: {', '.join(missing)}")

    def _get_connection(self):
        return psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)

    def _row_to_ticket(self, row: dict | None) -> Ticket | None:
        if not row:
            return None
        return Ticket(
            id=row.get("id"),
            title=row.get("title"),
            description=row.get("description"),
            category_id=row.get("category_id"),
            status_id=row.get("status_id"),
            latitude=row.get("latitude"),
            longitude=row.get("longitude"),
            address=row.get("address"),
            photo_url=row.get("photo_url"),
            ai_priority_suggestion=row.get("ai_priority_suggestion"),
            ai_category_confidence=row.get("ai_category_confidence"),
            admin_notes=row.get("admin_notes"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            is_deleted=row.get("is_deleted", False),
            status_name=row.get("status_name"),
            category_name=row.get("category_name"),
        )

    def create_ticket(self, data: dict) -> Ticket:
        for field in ("latitude", "longitude", "address", "photo_url"):
            if field in data and data[field] == "":
                data[field] = None
                
        defaults = {"category_id": None, "status_id": None, "address": None, "photo_url": None}
        for k, v in defaults.items():
            data.setdefault(k, v)

        query = """
            INSERT INTO tickets (title, description, category_id, status_id,
                                 latitude, longitude, address, photo_url)
            VALUES (%(title)s, %(description)s, %(category_id)s, %(status_id)s,
                    %(latitude)s, %(longitude)s, %(address)s, %(photo_url)s)
            RETURNING id;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, data)
                row = cur.fetchone()
                conn.commit()
                ticket_id = row["id"]
        return self.get_ticket(ticket_id)

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        query = """
            SELECT t.*, s.name AS status_name, c.name AS category_name
            FROM tickets t
            LEFT JOIN statuses s ON t.status_id = s.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = %s AND t.is_deleted = FALSE;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (ticket_id,))
                return self._row_to_ticket(cur.fetchone())

    def update_ticket(self, ticket_id: str, data: dict) -> Ticket | None:
        allowed = {"title", "description", "category_id", "status_id",
                   "latitude", "longitude", "address", "photo_url"}
        fields = {k: v for k, v in data.items() if k in allowed and v is not None}
        if not fields:
            return self.get_ticket(ticket_id)

        set_clause = ", ".join(f"{k} = %({k})s" for k in fields)
        fields["id"] = ticket_id
        query = f"""
            UPDATE tickets SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s AND is_deleted = FALSE
            RETURNING id;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, fields)
                row = cur.fetchone()
                conn.commit()
                if not row:
                    return None
        return self.get_ticket(ticket_id)

    def list_tickets(self, status_id: int = None, category_id: int = None) -> list[Ticket]:
        conditions = ["t.is_deleted = FALSE"]
        params = []
        if status_id is not None:
            conditions.append("t.status_id = %s")
            params.append(status_id)
        if category_id is not None:
            conditions.append("t.category_id = %s")
            params.append(category_id)
        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT t.*, s.name AS status_name, c.name AS category_name
            FROM tickets t
            LEFT JOIN statuses s ON t.status_id = s.id
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE {where_clause}
            ORDER BY t.created_at DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return [self._row_to_ticket(row) for row in cur.fetchall()]

    def update_ticket_status(self, ticket_id: str, status_id: int) -> Ticket | None:
        query = """
            UPDATE tickets
            SET status_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND is_deleted = FALSE
            RETURNING id;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (status_id, ticket_id))
                row = cur.fetchone()
                conn.commit()
                if not row:
                    return None
        return self.get_ticket(ticket_id)

    def update_ticket_notes(self, ticket_id: str, notes: str) -> Ticket | None:
        query = """
            UPDATE tickets
            SET admin_notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND is_deleted = FALSE
            RETURNING id;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (notes, ticket_id))
                row = cur.fetchone()
                conn.commit()
                if not row:
                    return None
        return self.get_ticket(ticket_id)
