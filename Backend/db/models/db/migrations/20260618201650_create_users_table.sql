-- migrate:up

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    role TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


-- migrate:down

DROP TABLE users;