-- Ενεργοποίηση της επέκτασης για την δημιουργία UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Δημιουργία πίνακα Καταστάσεων (Statuses)
CREATE TABLE IF NOT EXISTS statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 2. Δημιουργία πίνακα Κατηγοριών (Categories)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 3. Δημιουργία πίνακα Προβλημάτων/Αναφορών (Tickets)
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    status_id INTEGER REFERENCES statuses(id) ON DELETE SET NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,
    photo_url VARCHAR(512),
    ai_priority_suggestion VARCHAR(50),
    ai_category_confidence NUMERIC(5, 2),
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);