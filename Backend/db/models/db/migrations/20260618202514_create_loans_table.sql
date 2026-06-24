-- migrate:up

CREATE TABLE loans (
    id UUID PRIMARY KEY,

    farmer_id UUID REFERENCES farmers(id),

    amount NUMERIC(12,2),

    status TEXT,

    risk_score INTEGER,

    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE loans;
