-- migrate:up

ALTER TABLE loans
ADD COLUMN season_id UUID REFERENCES seasons(id);
-- migrate:down

DROP COLUMN season_id;