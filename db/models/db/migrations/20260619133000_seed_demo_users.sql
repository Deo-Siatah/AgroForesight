-- migrate:up

INSERT INTO users (id, email, password_hash, role, created_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'admin26@gmail.com', 'admin26', 'admin', NOW()),
    ('22222222-2222-2222-2222-222222222222', 'saccoadmin26@gmail.com', 'saccoadmin26', 'sacco_admin', NOW())
ON CONFLICT (email) DO NOTHING;

-- migrate:down

DELETE FROM users
WHERE email IN ('admin26@gmail.com', 'saccoadmin26@gmail.com');
