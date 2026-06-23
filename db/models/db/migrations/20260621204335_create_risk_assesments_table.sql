-- migrate:up

CREATE TYPE risk_level_enum AS ENUM (
    'low',
    'medium',
    'high'
);

CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY,

    loan_id UUID NOT NULL
        REFERENCES loans(id),

    season_id UUID NOT NULL
        REFERENCES seasons(id),

    score INTEGER NOT NULL,

    risk_level risk_level_enum NOT NULL,

    weather_risk INTEGER DEFAULT 0,

    season_risk INTEGER DEFAULT 0,

    harvest_risk INTEGER DEFAULT 0,

    report_risk INTEGER DEFAULT 0,

    compliance_risk INTEGER DEFAULT 0,

    needs_intervention BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_risk_assessments_loan
ON risk_assessments (loan_id);

CREATE INDEX idx_risk_assessments_season
ON risk_assessments (season_id);

CREATE INDEX idx_risk_assessments_created_at
ON risk_assessments (created_at);


-- migrate:down

DROP INDEX IF EXISTS idx_risk_assessments_created_at;
DROP INDEX IF EXISTS idx_risk_assessments_season;
DROP INDEX IF EXISTS idx_risk_assessments_loan;

DROP TABLE IF EXISTS risk_assessments;

DROP TYPE IF EXISTS risk_level_enum;