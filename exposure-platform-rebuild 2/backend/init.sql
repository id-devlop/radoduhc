
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role in ('underwriter','cuo','admin'))
);

CREATE TABLE IF NOT EXISTS audit_events (
  id BIGSERIAL PRIMARY KEY,
  type TEXT NOT NULL,
  user_name TEXT,
  user_role TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  payload JSONB
);

CREATE TABLE IF NOT EXISTS exposures (
  id BIGSERIAL PRIMARY KEY,
  lob TEXT NOT NULL,
  subclass TEXT,
  account_id TEXT,
  treaty_id TEXT,
  layer_id TEXT,
  jurisdiction TEXT,
  geography JSONB,
  metrics JSONB,        -- {tsi, aal, pml, turnover, gt, vessel_age, ...}
  meta JSONB,           -- {broker, client, policy_no, ...}
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bindings (
  id BIGSERIAL PRIMARY KEY,
  audit_id TEXT NOT NULL,
  bound_by TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO users (username, role) VALUES
  ('demo', 'underwriter')
ON CONFLICT (username) DO NOTHING;

INSERT INTO users (username, role) VALUES
  ('cuo-demo', 'cuo')
ON CONFLICT (username) DO NOTHING;
