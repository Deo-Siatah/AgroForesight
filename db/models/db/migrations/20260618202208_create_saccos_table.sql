-- migrate:up
CREATE TABLE saccos (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    county TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE saccos;