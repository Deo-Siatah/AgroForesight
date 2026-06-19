-- migrate:up
CREATE TABLE farmers (
    id UUID PRIMARY KEY,
    sacco_id UUID REFERENCES saccos(id),
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    national_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE farmers;