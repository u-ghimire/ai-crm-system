#!/usr/bin/env python3
"""
Migration Script: Company → Contacts → Deals Model
Date: 2024-11-15
Purpose: Safely migrate existing CRM data to new architecture
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'crm_database.db'

def connect_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def backup_database(conn):
    """Create backup before migration"""
    backup_path = DB_PATH.parent / f'crm_database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    backup_conn = sqlite3.connect(backup_path)
    conn.backup(backup_conn)
    backup_conn.close()
    print(f"✓ Database backed up to: {backup_path}")
    return backup_path

def run_migration_sql(conn):
    """Execute the migration SQL file"""
    sql_path = Path(__file__).parent / '001_company_contacts_deals_model.sql'
    
    with open(sql_path, 'r') as f:
        sql_script = f.read()
    
    # Execute SQL in chunks (split by semicolon)
    cursor = conn.cursor()
    
    # Remove comments and split by semicolon
    statements = []
    for line in sql_script.split('\n'):
        if line.strip() and not line.strip().startswith('--'):
            statements.append(line)
    
    sql_clean = '\n'.join(statements)
    
    try:
        cursor.executescript(sql_clean)
        conn.commit()
        print("✓ Database schema updated successfully")
    except Exception as e:
        print(f"✗ Error executing migration SQL: {e}")
        raise

def migrate_customers_to_contacts(conn):
    """
    Migrate customers table to contacts table
    Split 'name' field into first_name and last_name
    """
    cursor = conn.cursor()
    
    print("\n--- Migrating Customers → Contacts ---")
    
    # Get all customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    
    print(f"Found {len(customers)} customers to migrate")
    
    migrated = 0
    for customer in customers:
        # Split name into first and last
        name_parts = customer['name'].strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Check if already migrated
        cursor.execute("SELECT id FROM contacts WHERE id = ?", (customer['id'],))
        if cursor.fetchone():
            print(f"  Skip: Contact {customer['id']} already exists")
            continue
        
        try:
            cursor.execute('''
                INSERT INTO contacts (
                    id, first_name, last_name, email, phone, job_title,
                    company_id, status, lead_score, source, linkedin_url,
                    location, notes, assigned_to, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer['id'],
                first_name,
                last_name,
                customer['email'],
                customer['phone'],
                customer.get('job_title'),
                customer.get('company_id'),
                customer['status'],
                customer['lead_score'],
                customer.get('source'),
                customer.get('linkedin_url'),
                customer['location'],
                customer['notes'],
                customer['assigned_to'],
                customer['created_at'],
                customer['updated_at']
            ))
            migrated += 1
            print(f"  ✓ Migrated: {first_name} {last_name} (ID: {customer['id']})")
        except Exception as e:
            print(f"  ✗ Error migrating customer {customer['id']}: {e}")
    
    conn.commit()
    print(f"\n✓ Migrated {migrated} customers to contacts")

def migrate_opportunities_to_deals(conn):
    """
    Migrate opportunities table to deals table
    Link deals to companies and contacts properly
    """
    cursor = conn.cursor()
    
    print("\n--- Migrating Opportunities → Deals ---")
    
    # Get all opportunities from backup table or original
    try:
        cursor.execute("SELECT * FROM deals_backup")
    except sqlite3.OperationalError:
        cursor.execute("SELECT * FROM opportunities")
    
    opportunities = cursor.fetchall()
    
    print(f"Found {len(opportunities)} opportunities to migrate")
    
    migrated = 0
    for opp in opportunities:
        # Get the contact's company_id
        cursor.execute("SELECT company_id FROM contacts WHERE id = ?", (opp['customer_id'],))
        contact_row = cursor.fetchone()
        company_id = contact_row['company_id'] if contact_row and contact_row['company_id'] else opp.get('company_id')
        
        # If still no company_id, try to get from customer's company field
        if not company_id:
            cursor.execute("""
                SELECT c.id FROM companies c 
                JOIN customers cu ON cu.company = c.name 
                WHERE cu.id = ?
            """, (opp['customer_id'],))
            company_row = cursor.fetchone()
            company_id = company_row['id'] if company_row else None
        
        # Check if already migrated
        cursor.execute("SELECT id FROM deals WHERE id = ?", (opp['id'],))
        if cursor.fetchone():
            print(f"  Skip: Deal {opp['id']} already exists")
            continue
        
        try:
            # Generate deal number
            deal_number = f"DEAL-{datetime.now().year}-{opp['id']:04d}"
            
            cursor.execute('''
                INSERT INTO deals (
                    id, title, deal_number, company_id, primary_contact_id,
                    value, probability, stage, deal_stage, deal_type, deal_source,
                    expected_close_date, actual_close_date, status, lost_reason,
                    notes, assigned_to, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opp['id'],
                opp['title'],
                deal_number,
                company_id,
                opp['customer_id'],  # customer_id becomes primary_contact_id
                opp['value'],
                opp['probability'],
                opp['stage'],
                opp.get('deal_stage', 'Lead'),
                opp.get('deal_type'),
                opp.get('deal_source'),
                opp['expected_close_date'],
                opp.get('actual_close_date'),
                opp['status'],
                opp.get('lost_reason'),
                opp['notes'],
                opp.get('assigned_to'),
                opp['created_at'],
                opp['updated_at']
            ))
            
            # Create deal_contacts relationship
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
    print(f"\n✓ Migrated {migrated} opportunities to deals")

def create_sample_data(conn):
    """
    Create sample companies, contacts, and deals if database is empty
    """
    cursor = conn.cursor()
    
    # Check if we have data
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    
    if company_count > 0:
        print("\n✓ Database has existing data, skipping sample data creation")
        return
    
    print("\n--- Creating Sample Data ---")
    
    # Sample companies
    companies = [
        ('TechCorp Inc.', 'Technology', 'Enterprise', 5000000, 'https://techcorp.example.com', '+1-555-0100', 'info@techcorp.example.com'),
        ('Global Solutions Ltd.', 'Consulting', 'Mid-Market', 1000000, 'https://globalsolutions.example.com', '+1-555-0200', 'contact@globalsolutions.example.com'),
        ('Innovate Systems', 'Software', 'Startup', 250000, 'https://innovate.example.com', '+1-555-0300', 'hello@innovate.example.com'),
    ]
    
    for company in companies:
        cursor.execute('''
            INSERT INTO companies (name, industry, size, revenue, website, phone, email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', company)
    
    # Sample contacts
    contacts = [
        ('John', 'Smith', 'john.smith@techcorp.example.com', '+1-555-0101', 'VP of Sales', 1, 'Decision Maker'),
        ('Sarah', 'Johnson', 'sarah.j@techcorp.example.com', '+1-555-0102', 'IT Manager', 1, 'Technical Evaluator'),
        ('Michael', 'Chen', 'mchen@globalsolutions.example.com', '+1-555-0201', 'CEO', 2, 'Decision Maker'),
        ('Emily', 'Rodriguez', 'emily.r@innovate.example.com', '+1-555-0301', 'CTO', 3, 'Champion'),
    ]
    
    for contact in contacts:
        cursor.execute('''
            INSERT INTO contacts (first_name, last_name, email, phone, job_title, company_id, role, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'qualified')
        ''', contact)
    
    # Sample deals
    deals = [
        ('Enterprise License Agreement', 1, 1, 150000, 75, 'proposal', 'New Business'),
        ('Cloud Migration Project', 2, 3, 85000, 60, 'negotiation', 'New Business'),
        ('Software Integration', 3, 4, 45000, 80, 'qualified', 'New Business'),
    ]
    
    for i, deal in enumerate(deals, 1):
        deal_number = f"DEAL-{datetime.now().year}-{i:04d}"
        cursor.execute('''
            INSERT INTO deals (
                title, deal_number, company_id, primary_contact_id, value, 
                probability, stage, deal_type, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
        ''', (deal[0], deal_number, *deal[1:]))
        
        # Link contact to deal
        cursor.execute('''
            INSERT INTO deal_contacts (deal_id, contact_id, role, is_primary)
            VALUES (?, ?, 'Primary', 1)
        ''', (i, deal[2]))
    
    conn.commit()
    print("✓ Sample data created successfully")

def verify_migration(conn):
    """
    Verify the migration was successful
    """
    cursor = conn.cursor()
    
    print("\n--- Migration Verification ---")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    contact_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM deals")
    deal_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM deal_contacts")
    deal_contact_count = cursor.fetchone()[0]
    
    print(f"Companies: {company_count}")
    print(f"Contacts: {contact_count}")
    print(f"Deals: {deal_count}")
    print(f"Deal-Contact Links: {deal_contact_count}")
    
    # Test views
    try:
        cursor.execute("SELECT * FROM v_contacts_with_companies LIMIT 1")
        print("✓ View: v_contacts_with_companies working")
    except Exception as e:
        print(f"✗ View error: {e}")
    
    try:
        cursor.execute("SELECT * FROM v_deals_with_details LIMIT 1")
        print("✓ View: v_deals_with_details working")
    except Exception as e:
        print(f"✗ View error: {e}")
    
    try:
        cursor.execute("SELECT * FROM v_company_summary LIMIT 1")
        print("✓ View: v_company_summary working")
    except Exception as e:
        print(f"✗ View error: {e}")

def main():
    """
    Main migration function
    """
    print("=" * 70)
    print("CRM Migration: Company → Contacts → Deals Model")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = connect_db()
        
        # Create backup
        backup_path = backup_database(conn)
        
        # Run migration SQL
        run_migration_sql(conn)
        
        # Migrate existing data
        migrate_customers_to_contacts(conn)
        migrate_opportunities_to_deals(conn)
        
        # Create sample data if needed
        create_sample_data(conn)
        
        # Verify migration
        verify_migration(conn)
        
        conn.close()
        
        print("\n" + "=" * 70)
        print("✓ Migration completed successfully!")
        print(f"✓ Backup saved at: {backup_path}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print(f"✓ Database backup is safe at: {backup_path if 'backup_path' in locals() else 'Not created'}")
        raise

if __name__ == '__main__':
    main()
