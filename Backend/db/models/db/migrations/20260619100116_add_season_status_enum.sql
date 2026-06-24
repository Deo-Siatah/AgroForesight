-- migrate:up

CREATE TYPE season_status AS ENUM (
    'planned',
    'active',
    'harvested',
    'failed'
);

ALTER TABLE seasons ALTER COLUMN status TYPE season_status USING status::season_status;

-- migrate:down

ALTER TABLE seasons ALTER COLUMN status TYPE TEXT;
DROP TYPE season_status;