-- Migration: Implement Company → Contacts → Deals Model
-- Date: 2024-11-15
-- Purpose: Restructure CRM to use industry-standard data model

-- ============================================================================
-- STEP 1: Create new 'contacts' table
-- ============================================================================

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    mobile_phone TEXT,
    job_title TEXT,
    department TEXT,
    role TEXT,
    company_id INTEGER,
    linkedin_url TEXT,
    twitter_url TEXT,
    personal_website TEXT,
    status TEXT DEFAULT 'lead',
    lead_score REAL DEFAULT 0,
    source TEXT,
    assigned_to INTEGER,
    timezone TEXT,
    location TEXT,
    country TEXT,
    notes TEXT,
    tags TEXT,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_contacted_at TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- ============================================================================
-- STEP 3: Create new deals table
-- ============================================================================

CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    deal_number TEXT UNIQUE,
    company_id INTEGER NOT NULL,
    primary_contact_id INTEGER,
    value REAL DEFAULT 0,
    currency TEXT DEFAULT 'USD',
    probability REAL DEFAULT 0,
    stage TEXT DEFAULT 'lead',
    deal_stage TEXT DEFAULT 'Lead',
    deal_type TEXT,
    deal_source TEXT,
    expected_close_date DATE,
    actual_close_date DATE,
    days_in_stage INTEGER DEFAULT 0,
    status TEXT DEFAULT 'open',
    lost_reason TEXT,
    win_reason TEXT,
    discount_amount REAL DEFAULT 0,
    discount_percent REAL DEFAULT 0,
    assigned_to INTEGER,
    ai_predicted_close_date DATE,
    ai_win_probability REAL,
    ai_risk_score REAL,
    ai_next_action TEXT,
    notes TEXT,
    tags TEXT,
    custom_fields TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (primary_contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

-- ============================================================================
-- STEP 4: Create many-to-many relationship table for deals and contacts
-- ============================================================================

CREATE TABLE IF NOT EXISTS deal_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deal_id INTEGER NOT NULL,
    contact_id INTEGER NOT NULL,
    role TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    UNIQUE(deal_id, contact_id)
);

-- ============================================================================
-- STEP 5: Create indexes for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to);
CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status);

CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);
CREATE INDEX IF NOT EXISTS idx_companies_assigned_to ON companies(assigned_to);

CREATE INDEX IF NOT EXISTS idx_deals_company_id ON deals(company_id);
CREATE INDEX IF NOT EXISTS idx_deals_primary_contact_id ON deals(primary_contact_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_assigned_to ON deals(assigned_to);

CREATE INDEX IF NOT EXISTS idx_deal_contacts_deal_id ON deal_contacts(deal_id);
CREATE INDEX IF NOT EXISTS idx_deal_contacts_contact_id ON deal_contacts(contact_id);

-- ============================================================================
-- STEP 6: Create activity tracking table (unified timeline)
-- ============================================================================

CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_type TEXT NOT NULL,
    company_id INTEGER,
    contact_id INTEGER,
    deal_id INTEGER,
    user_id INTEGER,
    subject TEXT,
    description TEXT,
    outcome TEXT,
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_minutes INTEGER,
    sentiment TEXT,
    ai_summary TEXT,
    key_points TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_activities_company_id ON activities(company_id);
CREATE INDEX IF NOT EXISTS idx_activities_contact_id ON activities(contact_id);
CREATE INDEX IF NOT EXISTS idx_activities_deal_id ON activities(deal_id);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(activity_date);

-- ============================================================================
-- STEP 7: Create views for common queries
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_contacts_with_companies AS
SELECT 
    c.*,
    co.name as company_name,
    co.industry as company_industry,
    co.website as company_website,
    u.username as assigned_to_name
FROM contacts c
LEFT JOIN companies co ON c.company_id = co.id
LEFT JOIN users u ON c.assigned_to = u.id;

CREATE VIEW IF NOT EXISTS v_deals_with_details AS
SELECT 
    d.*,
    co.name as company_name,
    co.industry as company_industry,
    c.first_name || ' ' || c.last_name as primary_contact_name,
    c.email as primary_contact_email,
    c.job_title as primary_contact_title,
    u.username as assigned_to_name
FROM deals d
LEFT JOIN companies co ON d.company_id = co.id
LEFT JOIN contacts c ON d.primary_contact_id = c.id
LEFT JOIN users u ON d.assigned_to = u.id;

CREATE VIEW IF NOT EXISTS v_company_summary AS
SELECT 
    co.*,
    COUNT(DISTINCT c.id) as contact_count,
    COUNT(DISTINCT d.id) as deal_count,
    SUM(CASE WHEN d.status = 'open' THEN d.value ELSE 0 END) as open_deal_value,
    SUM(CASE WHEN d.status = 'won' THEN d.value ELSE 0 END) as won_deal_value
FROM companies co
LEFT JOIN contacts c ON c.company_id = co.id
LEFT JOIN deals d ON d.company_id = co.id
GROUP BY co.id;
