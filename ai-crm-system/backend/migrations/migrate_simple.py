#!/usr/bin/env python3
"""
Simplified Migration Script: Company → Contacts → Deals Model
Handles existing tables more gracefully
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'crm_database.db'

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def backup_database(conn):
    backup_path = DB_PATH.parent / f'crm_database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    print(f"✓ Database backed up to: {backup_path}")
    return backup_path

def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def create_contacts_table(cursor):
    if table_exists(cursor, 'contacts'):
        print("  Table 'contacts' already exists, skipping")
        return
    
    print("  Creating 'contacts' table...")
    cursor.execute('''
        CREATE TABLE contacts (
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
        )
    ''')
    print("  ✓ Created 'contacts' table")

def create_deals_table(cursor):
    if table_exists(cursor, 'deals'):
        print("  Table 'deals' already exists, skipping")
        return
    
    print("  Creating 'deals' table...")
    cursor.execute('''
        CREATE TABLE deals (
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
        )
    ''')
    print("  ✓ Created 'deals' table")

def create_deal_contacts_table(cursor):
    if table_exists(cursor, 'deal_contacts'):
        print("  Table 'deal_contacts' already exists, skipping")
        return
    
    print("  Creating 'deal_contacts' table...")
    cursor.execute('''
        CREATE TABLE deal_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id INTEGER NOT NULL,
            contact_id INTEGER NOT NULL,
            role TEXT,
            is_primary BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE CASCADE,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
            UNIQUE(deal_id, contact_id)
        )
    ''')
    print("  ✓ Created 'deal_contacts' table")

def create_activities_table(cursor):
    if table_exists(cursor, 'activities'):
        print("  Table 'activities' already exists, skipping")
        return
    
    print("  Creating 'activities' table...")
    cursor.execute('''
        CREATE TABLE activities (
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
        )
    ''')
    print("  ✓ Created 'activities' table")

def create_indexes(cursor):
    print("  Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON contacts(company_id)",
        "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)",
        "CREATE INDEX IF NOT EXISTS idx_contacts_assigned_to ON contacts(assigned_to)",
        "CREATE INDEX IF NOT EXISTS idx_contacts_status ON contacts(status)",
        "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)",
        "CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry)",
        "CREATE INDEX IF NOT EXISTS idx_companies_assigned_to ON companies(assigned_to)",
        "CREATE INDEX IF NOT EXISTS idx_deals_company_id ON deals(company_id)",
        "CREATE INDEX IF NOT EXISTS idx_deals_primary_contact_id ON deals(primary_contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage)",
        "CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status)",
        "CREATE INDEX IF NOT EXISTS idx_deals_assigned_to ON deals(assigned_to)",
        "CREATE INDEX IF NOT EXISTS idx_deal_contacts_deal_id ON deal_contacts(deal_id)",
        "CREATE INDEX IF NOT EXISTS idx_deal_contacts_contact_id ON deal_contacts(contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_activities_company_id ON activities(company_id)",
        "CREATE INDEX IF NOT EXISTS idx_activities_contact_id ON activities(contact_id)",
        "CREATE INDEX IF NOT EXISTS idx_activities_deal_id ON activities(deal_id)",
        "CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type)",
        "CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(activity_date)",
    ]
    
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
        except Exception as e:
            print(f"    Warning: {e}")
    
    print("  ✓ Indexes created")

def migrate_customers_to_contacts(conn):
    cursor = conn.cursor()
    
    print("\n--- Migrating Customers → Contacts ---")
    
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    
    print(f"Found {len(customers)} customers to migrate")
    
    migrated = 0
    for customer in customers:
        # Check if already migrated
        cursor.execute("SELECT id FROM contacts WHERE id = ?", (customer['id'],))
        if cursor.fetchone():
            continue
        
        name_parts = customer['name'].strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Get values with default fallbacks
        job_title = customer['job_title'] if 'job_title' in customer.keys() else None
        company_id = customer['company_id'] if 'company_id' in customer.keys() else None
        source = customer['source'] if 'source' in customer.keys() else None
        linkedin_url = customer['linkedin_url'] if 'linkedin_url' in customer.keys() else None
        
        try:
            cursor.execute('''
                INSERT INTO contacts (
                    id, first_name, last_name, email, phone, job_title,
                    company_id, status, lead_score, source, linkedin_url,
                    location, notes, assigned_to, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer['id'], first_name, last_name, customer['email'],
                customer['phone'], job_title, company_id,
                customer['status'], customer['lead_score'], source,
                linkedin_url, customer['location'], customer['notes'],
                customer['assigned_to'], customer['created_at'], customer['updated_at']
            ))
            migrated += 1
            print(f"  ✓ Migrated: {first_name} {last_name} (ID: {customer['id']})")
        except Exception as e:
            print(f"  ✗ Error migrating customer {customer['id']}: {e}")
    
    conn.commit()
    print(f"✓ Migrated {migrated} customers to contacts")

def migrate_opportunities_to_deals(conn):
    cursor = conn.cursor()
    
    print("\n--- Migrating Opportunities → Deals ---")
    
    cursor.execute("SELECT * FROM opportunities")
    opportunities = cursor.fetchall()
    
    print(f"Found {len(opportunities)} opportunities to migrate")
    
    migrated = 0
    for opp in opportunities:
        # Check if already migrated
        cursor.execute("SELECT id FROM deals WHERE id = ?", (opp['id'],))
        if cursor.fetchone():
            continue
        
        # Get contact's company_id
        cursor.execute("SELECT company_id FROM contacts WHERE id = ?", (opp['customer_id'],))
        contact_row = cursor.fetchone()
        
        # Get company_id with fallbacks
        company_id = None
        if contact_row and contact_row['company_id']:
            company_id = contact_row['company_id']
        elif 'company_id' in opp.keys() and opp['company_id']:
            company_id = opp['company_id']
        
        if not company_id:
            print(f"  ! Opportunity {opp['id']} has no company, skipping")
            continue
        
        # Get optional fields with fallbacks
        deal_stage = opp['deal_stage'] if 'deal_stage' in opp.keys() else 'Lead'
        deal_type = opp['deal_type'] if 'deal_type' in opp.keys() else None
        deal_source = opp['deal_source'] if 'deal_source' in opp.keys() else None
        actual_close_date = opp['actual_close_date'] if 'actual_close_date' in opp.keys() else None
        lost_reason = opp['lost_reason'] if 'lost_reason' in opp.keys() else None
        assigned_to = opp['assigned_to'] if 'assigned_to' in opp.keys() else None
        
        try:
            deal_number = f"DEAL-{datetime.now().year}-{opp['id']:04d}"
            
            cursor.execute('''
                INSERT INTO deals (
                    id, title, deal_number, company_id, primary_contact_id,
                    value, probability, stage, deal_stage, deal_type, deal_source,
                    expected_close_date, actual_close_date, status, lost_reason,
                    notes, assigned_to, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp['id'], opp['title'], deal_number, company_id, opp['customer_id'],
                opp['value'], opp['probability'], opp['stage'], deal_stage,
                deal_type, deal_source, opp['expected_close_date'],
                actual_close_date, opp['status'], lost_reason,
                opp['notes'], assigned_to, opp['created_at'], opp['updated_at']
            ))
            
            # Link contact to deal
            if opp['customer_id']:
                cursor.execute('''
                    INSERT OR IGNORE INTO deal_contacts (deal_id, contact_id, role, is_primary)
                    VALUES (?, ?, ?, ?)
                ''', (opp['id'], opp['customer_id'], 'Primary', 1))
            
            migrated += 1
            print(f"  ✓ Migrated: {opp['title']} (ID: {opp['id']})")
        except Exception as e:
            print(f"  ✗ Error migrating opportunity {opp['id']}: {e}")
    
    conn.commit()
    print(f"✓ Migrated {migrated} opportunities to deals")

def main():
    print("=" * 70)
    print("CRM Migration: Company → Contacts → Deals Model")
    print("=" * 70)
    
    try:
        conn = connect_db()
        backup_path = backup_database(conn)
        cursor = conn.cursor()
        
        print("\n--- Creating New Tables ---")
        create_contacts_table(cursor)
        create_deals_table(cursor)
        create_deal_contacts_table(cursor)
        create_activities_table(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # Migrate data
        migrate_customers_to_contacts(conn)
        migrate_opportunities_to_deals(conn)
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✓ Migration completed successfully!")
        print(f"✓ Backup saved at: {backup_path}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
