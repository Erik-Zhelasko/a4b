-- TEAM SETUP FILE: Only objects ADDED by the team go here

CREATE TABLE IF NOT EXISTS app_user (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin','viewer'))
);

-- Replace this hash with a real one using generate_password_hash()
INSERT INTO app_user (username, password_hash, role)
VALUES
('admin', 'scrypt:32768:8:1$R50ftwA8fqFdFvP8$8c797b1e96c59c9751cc853403bcd5f33f04519f6cb98524c5087f56dcf33b8e482d9f9a51cf9303a3f88b34c2d658de80e320a1f1a189eb33dc581797ca6d14', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Example index choices (required in README justification)
CREATE INDEX IF NOT EXISTS idx_employee_name 
    ON employee (lname, fname);

CREATE INDEX IF NOT EXISTS idx_works_on_essn
    ON works_on (essn);

INSERT INTO app_user (username, password_hash, role)
VALUES ('viewer', 'scrypt:32768:8:1$T7lEUlGSypoIFbXy$92ade96a579e98aa69ca3dfcb35d4a8bd20ed6105ee2dc353a157ae3a211be7205113d85c1e45f99d18dd7fb3a0b53eceeccf1d65983c9e26830b3ee79c50584', 'viewer')
ON CONFLICT (username) DO NOTHING;