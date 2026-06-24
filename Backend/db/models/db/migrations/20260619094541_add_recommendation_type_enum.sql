-- migrate:up
CREATE TYPE recommendation_type AS ENUM (
  'planting',
  'fertilizer',
  'weeding',
  'pest',
  'harvest',
  'weather',
  'finance'
);

-- Convert the existing TEXT column to the enum type
ALTER TABLE recommendations 
ALTER COLUMN recommendation_type TYPE recommendation_type USING recommendation_type::recommendation_type;

-- migrate:down
ALTER TABLE recommendations 
ALTER COLUMN recommendation_type TYPE TEXT;

DROP TYPE recommendation_type;