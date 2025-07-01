
-- Clients table: Organizations using your system
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    organization_name TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Identities table: People whose faces are enrolled
CREATE TABLE identities (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cameras table: Cameras assigned to gates for each client
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    roll TEXT NOT NULL, -- entry or exit
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    gate TEXT NOT NULL,
    camera_location TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create entry and exit log table that store who and when and where enter or exit a gate
CREATE TABLE access_logs  (
    id SERIAL PRIMARY KEY,
    identity_id INTEGER REFERENCES identities(id) ON DELETE CASCADE,
    camera_id INTEGER REFERENCES cameras(id) ON DELETE SET NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type TEXT NOT NULL, -- 'entry', 'exit'
    detection_confidence REAL NOT NULL,
    processing_time_ms REAL NOT NULL
);

-- Add indexes to improve foreign key lookup performance
CREATE INDEX idx_identities_client_id ON identities(client_id);
CREATE INDEX idx_cameras_client_id ON cameras(client_id);
CREATE INDEX idx_access_logs_identity_id ON access_logs(identity_id);
CREATE INDEX idx_access_logs_camera_id ON access_logs(camera_id);
