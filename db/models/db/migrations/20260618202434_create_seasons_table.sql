-- migrate:up

CREATE TABLE seasons (
    id UUID PRIMARY KEY,

    farm_id UUID REFERENCES farms(id),

    crop_type TEXT,

    planting_date DATE,

    expected_harvest_date DATE,

    status TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE seasons;