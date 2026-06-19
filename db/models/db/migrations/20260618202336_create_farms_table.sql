-- migrate:up
CREATE TABLE farms (
    id UUID PRIMARY KEY,
    farmer_id UUID REFERENCES farmers(id),

    name TEXT,
    county TEXT,

    acreage NUMERIC(10,2),

    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE farms;