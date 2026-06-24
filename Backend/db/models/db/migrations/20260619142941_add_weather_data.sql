-- migrate:up
CREATE TABLE weather_snapshots (
    id UUID PRIMARY KEY,

    farm_id UUID NOT NULL REFERENCES farms(id),

    date DATE NOT NULL,

    rainfall_mm NUMERIC(10,2),

    temperature_c NUMERIC(10,2),

    humidity_percent NUMERIC(10,2),

    source TEXT DEFAULT 'open-meteo',

    created_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE weather_snapshots;