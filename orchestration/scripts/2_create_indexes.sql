-- Δημιουργία Indexes για γρήγορη αναζήτηση και φιλτράρισμα
CREATE INDEX idx_tickets_status ON tickets(status_id);
CREATE INDEX idx_tickets_category ON tickets(category_id);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_is_deleted ON tickets(is_deleted);
