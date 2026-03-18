-- Where Next: Supabase Schema
-- Founder career migration tracker

-- ============================================
-- FOUNDERS TABLE
-- ============================================
CREATE TABLE founders (
  id TEXT PRIMARY KEY,                    -- lowercase-hyphenated slug
  name TEXT NOT NULL,
  primary_sector TEXT NOT NULL DEFAULT 'Other',
  source_url TEXT,
  verified DATE,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- ROLES TABLE (career entries)
-- ============================================
CREATE TABLE roles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  founder_id TEXT NOT NULL REFERENCES founders(id) ON DELETE CASCADE,
  company TEXT NOT NULL,
  role TEXT NOT NULL,
  sector TEXT NOT NULL,
  start_year INT,
  end_year INT,                            -- NULL = current
  note TEXT,
  sort_order INT DEFAULT 0,                -- for ordering roles chronologically
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- SECTOR SWITCHES TABLE
-- ============================================
CREATE TABLE sector_switches (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  founder_id TEXT NOT NULL REFERENCES founders(id) ON DELETE CASCADE,
  from_sector TEXT NOT NULL,
  to_sector TEXT NOT NULL,
  year INT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- USER CHARTS (saved chart configurations)
-- ============================================
CREATE TABLE user_charts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  name TEXT NOT NULL DEFAULT 'My Chart',
  founder_ids TEXT[] NOT NULL DEFAULT '{}', -- array of founder IDs on chart
  is_public BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_roles_founder ON roles(founder_id);
CREATE INDEX idx_sector_switches_founder ON sector_switches(founder_id);
CREATE INDEX idx_user_charts_user ON user_charts(user_id);
CREATE INDEX idx_founders_sector ON founders(primary_sector);
CREATE INDEX idx_founders_name ON founders(name);

-- Full text search on founder names
ALTER TABLE founders ADD COLUMN fts tsvector 
  GENERATED ALWAYS AS (to_tsvector('english', name)) STORED;
CREATE INDEX idx_founders_fts ON founders USING gin(fts);

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Founders: anyone can read, authenticated users can insert
ALTER TABLE founders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "founders_read" ON founders FOR SELECT USING (true);
CREATE POLICY "founders_insert" ON founders FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "founders_update" ON founders FOR UPDATE USING (auth.uid() = created_by);

-- Roles: same as founders
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "roles_read" ON roles FOR SELECT USING (true);
CREATE POLICY "roles_insert" ON roles FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Sector switches: same
ALTER TABLE sector_switches ENABLE ROW LEVEL SECURITY;
CREATE POLICY "switches_read" ON sector_switches FOR SELECT USING (true);
CREATE POLICY "switches_insert" ON sector_switches FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- User charts: owner can CRUD, public charts readable by all
ALTER TABLE user_charts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "charts_read_own" ON user_charts FOR SELECT USING (auth.uid() = user_id OR is_public = true);
CREATE POLICY "charts_insert" ON user_charts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "charts_update" ON user_charts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "charts_delete" ON user_charts FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- ANON ACCESS (for unauthenticated browsing)
-- ============================================
-- Allow anon to read founders, roles, switches (public data)
CREATE POLICY "founders_anon_read" ON founders FOR SELECT TO anon USING (true);
CREATE POLICY "roles_anon_read" ON roles FOR SELECT TO anon USING (true);
CREATE POLICY "switches_anon_read" ON sector_switches FOR SELECT TO anon USING (true);

-- ============================================
-- UPDATED_AT TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER founders_updated_at BEFORE UPDATE ON founders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER user_charts_updated_at BEFORE UPDATE ON user_charts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
