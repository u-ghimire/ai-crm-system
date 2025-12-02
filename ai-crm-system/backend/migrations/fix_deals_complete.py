#!/usr/bin/env python3
"""
Fix Deals Table and Complete Migration
Resolves the duplicate deals table issue
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
    backup_path = DB_PATH.parent / f'crm_database_backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    print(f"✓ Database backed up to: {backup_path}")
    return backup_path

def fix_deals_table(conn):
    """
    Drop old deals table and recreate with proper structure
    """
    cursor = conn.cursor()
    
    print("\n--- Fixing Deals Table ---")
    
    # Check if old deals table has data
    cursor.execute("SELECT COUNT(*) FROM deals")
    old_count = cursor.fetchone()[0]
    
    if old_count > 0:
        print(f"  Warning: Old deals table has {old_count} records")
        # Backup to deals_old first
        cursor.execute("DROP TABLE IF EXISTS deals_old")
        cursor.execute("ALTER TABLE deals RENAME TO deals_old")
        print(f"  ✓ Backed up {old_count} records to deals_old")
    else:
        cursor.execute("DROP TABLE IF EXISTS deals")
        print("  ✓ Dropped empty old deals table")
    
    # Create new deals table with proper structure
    print("  Creating new deals table...")
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
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_company_id ON deals(company_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_primary_contact_id ON deals(primary_contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_deals_status ON deals(status)")
    
    conn.commit()
    print("  ✓ New deals table created with proper structure")

def migrate_opportunities_to_deals(conn):
    """
    Migrate opportunities to new deals table
    """
    cursor = conn.cursor()
    
    print("\n--- Migrating Opportunities → Deals ---")
    
    cursor.execute("SELECT * FROM opportunities")
    opportunities = cursor.fetchall()
    
    print(f"Found {len(opportunities)} opportunities to migrate")
    
    migrated = 0
    skipped = 0
    
    for opp in opportunities:
        # Get contact's company_id
        cursor.execute("SELECT company_id FROM contacts WHERE id = ?", (opp['customer_id'],))
        contact_row = cursor.fetchone()
        
        company_id = None
        if contact_row and contact_row['company_id']:
            company_id = contact_row['company_id']
        elif 'company_id' in opp.keys() and opp['company_id']:
            company_id = opp['company_id']
        
        if not company_id:
            # Try to get customer's company and find/create company
            cursor.execute("SELECT company FROM customers WHERE id = ?", (opp['customer_id'],))
            customer_row = cursor.fetchone()
            if customer_row and customer_row['company']:
                # Find or create company
                cursor.execute("SELECT id FROM companies WHERE name = ?", (customer_row['company'],))
                company_row = cursor.fetchone()
                if company_row:
                    company_id = company_row['id']
                else:
                    # Create company
                    cursor.execute("INSERT INTO companies (name) VALUES (?)", (customer_row['company'],))
                    company_id = cursor.lastrowid
                    print(f"  ✓ Created company: {customer_row['company']}")
                    
                    # Update contact with company_id
                    cursor.execute("UPDATE contacts SET company_id = ? WHERE id = ?", 
                                 (company_id, opp['customer_id']))
        
        if not company_id:
            print(f"  ! Skipping opportunity {opp['id']}: {opp['title']} (no company)")
            skipped += 1
            continue
        
        # Get optional fields
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
            print(f"  ✓ Migrated: {opp['title']} → {deal_number}")
        except Exception as e:
            print(f"  ✗ Error migrating opportunity {opp['id']}: {e}")
    
    conn.commit()
    print(f"\n✓ Migrated {migrated} opportunities to deals ({skipped} skipped)")

def verify_structure(conn):
    """
    Verify the final database structure
    """
    cursor = conn.cursor()
    
    print("\n--- Verification ---")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM companies")
    companies = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM deals")
    deals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM deal_contacts")
    deal_contacts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM activities")
    activities = cursor.fetchone()[0]
    
    print(f"Companies: {companies}")
    print(f"Contacts: {contacts}")
    print(f"Deals: {deals}")
    print(f"Deal-Contact Links: {deal_contacts}")
    print(f"Activities: {activities}")
    
    # Show sample data
    if deals > 0:
        print("\n--- Sample Deal ---")
        cursor.execute("""
            SELECT d.deal_number, d.title, d.value, d.stage,
                   c.name as company_name,
                   co.first_name || ' ' || co.last_name as contact_name
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN contacts co ON d.primary_contact_id = co.id
            LIMIT 1
        """)
        deal = cursor.fetchone()
        if deal:
            print(f"  Deal: {deal['deal_number']}")
            print(f"  Title: {deal['title']}")
            print(f"  Value: ${deal['value']:,.2f}")
            print(f"  Stage: {deal['stage']}")
            print(f"  Company: {deal['company_name']}")
            print(f"  Contact: {deal['contact_name']}")

def main():
    print("=" * 70)
    print("Fixing Deals Table & Completing Migration")
    print("=" * 70)
    
    try:
        conn = connect_db()
        backup_path = backup_database(conn)
        
        fix_deals_table(conn)
        migrate_opportunities_to_deals(conn)
        verify_structure(conn)
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✓ Migration completed successfully!")
        print(f"✓ Backup: {backup_path}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
