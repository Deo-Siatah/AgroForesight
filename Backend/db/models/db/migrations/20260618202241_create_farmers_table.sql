-- migrate:up
CREATE TABLE farmers (
    id UUID PRIMARY KEY,
    sacco_id UUID REFERENCES saccos(id),
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    national_id TEXT,
    CONSTRAINT uq_farmers_phone UNIQUE (phone),
    CONSTRAINT uq_farmers_national_id UNIQUE (national_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE farmers;