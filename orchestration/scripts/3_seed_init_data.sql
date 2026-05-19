-- Αρχικοποίηση Δεδομένων (Seed Data)

-- Εισαγωγή των προκαθορισμένων Καταστάσεων
INSERT INTO statuses (name, description) VALUES
    ('Reported', 'The problem was reported by a citizen.'),
    ('In Progress', 'The problem has been checked and actions are being taken for resolution.'),
    ('Resolved', 'The problem has been successfully addressed.'),
    ('Rejected', 'The report is invalid or not feasible for resolution.')
ON CONFLICT (name) DO NOTHING;

-- Εισαγωγή των προκαθορισμένων Κατηγοριών
INSERT INTO categories (name, description) VALUES
    ('Roads', 'Potholes, damaged sidewalks, road surface deterioration.'),
    ('Street Lighting', 'Burned-out bulbs, faults in lighting poles.'),
    ('Cleanliness', 'Dumped waste, large objects, litter.'),
    ('Water Supply / Sewage', 'Water leaks, broken pipes, blocked manholes.'),
    ('Green Spaces', 'Tree cutting, park maintenance.'),
    ('Abandoned Vehicles', 'Vehicles without plates or abandoned for a long time.'),
    ('Other', 'Anything that does not fit into the above categories.')
ON CONFLICT (name) DO NOTHING;