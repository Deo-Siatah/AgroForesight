-- migrate:up

CREATE TYPE user_role AS ENUM (
    'admin',
    'sacco_admin',
    'farmer',
    'extension_officer'
);

ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role;

-- migrate:down

ALTER TABLE users ALTER COLUMN role TYPE TEXT;
DROP TYPE user_role;