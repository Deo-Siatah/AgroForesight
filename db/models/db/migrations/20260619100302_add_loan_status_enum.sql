-- migrate:up

CREATE TYPE loan_status AS ENUM (
    'pending',
    'approved',
    'disbursed',
    'active',
    'repaid',
    'defaulted',
    'rejected'
);

ALTER TABLE loans ALTER COLUMN status TYPE loan_status USING status::loan_status;

-- migrate:down

ALTER TABLE loans ALTER COLUMN status TYPE TEXT;
DROP TYPE loan_status;