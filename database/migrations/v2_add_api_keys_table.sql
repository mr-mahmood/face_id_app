-- Add API Keys table for client authentication
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,
    api_key TEXT UNIQUE NOT NULL,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (client_id, api_key)
);

-- Add indexes for better performance
CREATE INDEX idx_api_keys_client_id ON api_keys(client_id);
CREATE INDEX idx_api_keys_api_key ON api_keys(api_key);
CREATE INDEX idx_api_keys_is_active ON api_keys(is_active);
