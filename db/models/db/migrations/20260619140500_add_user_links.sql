-- migrate:up

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS sacco_id UUID REFERENCES saccos(id),
    ADD COLUMN IF NOT EXISTS farmer_id UUID REFERENCES farmers(id);

-- migrate:down

ALTER TABLE users
    DROP COLUMN IF EXISTS farmer_id,
    DROP COLUMN IF EXISTS sacco_id;
