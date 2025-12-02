-- Migration: Add Core CRM Features
-- Date: 2025-11-11
-- Description: Add companies table, enhance deals and tasks tables

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    industry TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    postal_code TEXT,
    employee_count INTEGER,
    annual_revenue REAL,
    description TEXT,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Add company_id to customers table if not exists
ALTER TABLE customers ADD COLUMN company_id INTEGER REFERENCES companies(id);

-- Enhance deals table with more fields
ALTER TABLE opportunities ADD COLUMN deal_stage TEXT DEFAULT 'lead';
ALTER TABLE opportunities ADD COLUMN probability REAL DEFAULT 0.0;
ALTER TABLE opportunities ADD COLUMN expected_close_date DATE;
ALTER TABLE opportunities ADD COLUMN actual_close_date DATE;
ALTER TABLE opportunities ADD COLUMN deal_type TEXT; -- new_business, renewal, upsell
ALTER TABLE opportunities ADD COLUMN deal_source TEXT; -- inbound, outbound, referral, etc
ALTER TABLE opportunities ADD COLUMN notes TEXT;
ALTER TABLE opportunities ADD COLUMN lost_reason TEXT;
ALTER TABLE opportunities ADD COLUMN company_id INTEGER REFERENCES companies(id);

-- Enhance tasks table with more fields
ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'; -- low, medium, high, urgent
ALTER TABLE tasks ADD COLUMN category TEXT; -- call, email, meeting, follow_up, demo, etc
ALTER TABLE tasks ADD COLUMN customer_id INTEGER REFERENCES customers(id);
ALTER TABLE tasks ADD COLUMN opportunity_id INTEGER REFERENCES opportunities(id);
ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN reminder_at TIMESTAMP;
ALTER TABLE tasks ADD COLUMN notes TEXT;

-- Create deal_stages reference table
CREATE TABLE IF NOT EXISTS deal_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    order_index INTEGER NOT NULL,
    probability REAL DEFAULT 0.0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default deal stages
INSERT INTO deal_stages (name, order_index, probability, is_active) VALUES
('Lead', 1, 10.0, 1),
('Qualified', 2, 25.0, 1),
('Proposal', 3, 50.0, 1),
('Negotiation', 4, 75.0, 1),
('Closed Won', 5, 100.0, 1),
('Closed Lost', 6, 0.0, 1);

-- Create email_integrations table for future use
CREATE TABLE IF NOT EXISTS email_integrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    provider TEXT NOT NULL, -- gmail, outlook
    email_address TEXT NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create email_messages table for future use
CREATE TABLE IF NOT EXISTS email_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    integration_id INTEGER NOT NULL,
    message_id TEXT UNIQUE NOT NULL,
    thread_id TEXT,
    subject TEXT,
    from_address TEXT,
    to_addresses TEXT,
    cc_addresses TEXT,
    body_text TEXT,
    body_html TEXT,
    sent_at TIMESTAMP,
    customer_id INTEGER,
    opportunity_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (integration_id) REFERENCES email_integrations(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
);

-- Create attachments table for future use
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    mime_type TEXT,
    uploaded_by INTEGER NOT NULL,
    customer_id INTEGER,
    opportunity_id INTEGER,
    task_id INTEGER,
    email_message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (email_message_id) REFERENCES email_messages(id)
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    customer_id INTEGER,
    opportunity_id INTEGER,
    company_id INTEGER,
    is_pinned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (opportunity_id) REFERENCES opportunities(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Create activity_log table for comprehensive tracking
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    action_type TEXT NOT NULL, -- created, updated, deleted, viewed, emailed, called, etc
    entity_type TEXT NOT NULL, -- customer, opportunity, task, company, etc
    entity_id INTEGER NOT NULL,
    description TEXT,
    metadata TEXT, -- JSON string with additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_stage ON opportunities(deal_stage);
CREATE INDEX IF NOT EXISTS idx_opportunities_company ON opportunities(company_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_customer ON tasks(customer_id);
CREATE INDEX IF NOT EXISTS idx_tasks_opportunity ON tasks(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_customer ON notes(customer_id);
CREATE INDEX IF NOT EXISTS idx_notes_opportunity ON notes(opportunity_id);
