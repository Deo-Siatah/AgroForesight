-- migrate:up

CREATE TABLE recommendations (
    id UUID PRIMARY KEY,

    season_id UUID REFERENCES seasons(id),

    recommendation_type TEXT,

    message TEXT,

    generated_at TIMESTAMP DEFAULT NOW()
);

-- migrate:down

DROP TABLE recommendations;
