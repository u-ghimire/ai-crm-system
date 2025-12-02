# modules/database_enhanced.py
"""
Enhanced Database Module with additional CRM features:
- Companies table (separate from contacts)
- Deals/Pipeline management
- Tasks with better assignment
- File attachments
- Activity logs
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class EnhancedDatabase:
    """Enhanced database operations for CRM"""
    
    def __init__(self, db_path='crm_database.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_enhanced_tables(self):
        """Create additional tables for enhanced CRM features"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Companies table (separate from contacts)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                industry TEXT,
                size TEXT,
                revenue REAL,
                website TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                postal_code TEXT,
                description TEXT,
                status TEXT DEFAULT 'active',
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_to) REFERENCES users(id)
            )
        ''')
        
        # Update customers to link with companies
        # Check if company_id column exists, if not add it
        cursor.execute("PRAGMA table_info(customers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'company_id' not in columns:
            cursor.execute('''
                ALTER TABLE customers ADD COLUMN company_id INTEGER REFERENCES companies(id)
            ''')
        
        if 'job_title' not in columns:
            cursor.execute('''
                ALTER TABLE customers ADD COLUMN job_title TEXT
            ''')
        
        if 'source' not in columns:
            cursor.execute('''
                ALTER TABLE customers ADD COLUMN source TEXT
            ''')
        
        if 'linkedin_url' not in columns:
            cursor.execute('''
                ALTER TABLE customers ADD COLUMN linkedin_url TEXT
            ''')
        
        # Deals/Pipeline table (enhanced opportunities)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                company_id INTEGER,
                contact_id INTEGER,
                value REAL,
                stage TEXT DEFAULT 'lead',
                probability REAL DEFAULT 0,
                expected_close_date DATE,
                actual_close_date DATE,
                lost_reason TEXT,
                status TEXT DEFAULT 'open',
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                FOREIGN KEY (contact_id) REFERENCES customers(id),
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        ''')
        
        # Deal stages history (for tracking movement through pipeline)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_stage_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id INTEGER NOT NULL,
                from_stage TEXT,
                to_stage TEXT,
                changed_by INTEGER,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (deal_id) REFERENCES deals(id),
                FOREIGN KEY (changed_by) REFERENCES users(id)
            )
        ''')
        
        # Enhanced tasks table additions
        cursor.execute("PRAGMA table_info(tasks)")
        task_columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_by' not in task_columns:
            cursor.execute('''
                ALTER TABLE tasks ADD COLUMN assigned_by INTEGER REFERENCES users(id)
            ''')
        
        if 'related_deal_id' not in task_columns:
            cursor.execute('''
                ALTER TABLE tasks ADD COLUMN related_deal_id INTEGER REFERENCES deals(id)
            ''')
        
        if 'reminder_sent' not in task_columns:
            cursor.execute('''
                ALTER TABLE tasks ADD COLUMN reminder_sent BOOLEAN DEFAULT 0
            ''')
        
        # Files/Attachments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                entity_type TEXT,
                entity_id INTEGER,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
        ''')
        
        # Notes table (separate from inline notes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_pinned BOOLEAN DEFAULT 0,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        # Activity log (for tracking all changes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type TEXT,
                entity_type TEXT,
                entity_id INTEGER,
                description TEXT,
                metadata TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Email tracking table (for email integration)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE,
                subject TEXT,
                from_email TEXT,
                to_email TEXT,
                cc_email TEXT,
                body TEXT,
                html_body TEXT,
                direction TEXT,
                related_contact_id INTEGER,
                related_company_id INTEGER,
                related_deal_id INTEGER,
                email_provider TEXT,
                received_at TIMESTAMP,
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (related_contact_id) REFERENCES customers(id),
                FOREIGN KEY (related_company_id) REFERENCES companies(id),
                FOREIGN KEY (related_deal_id) REFERENCES deals(id)
            )
        ''')
        
        # User permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                permission_name TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                granted_by INTEGER,
                granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (granted_by) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Company operations
    def add_company(self, data: Dict) -> int:
        """Add new company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO companies (
                name, industry, size, revenue, website, phone, email,
                address, city, state, country, postal_code, description, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('industry'),
            data.get('size'),
            data.get('revenue'),
            data.get('website'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            data.get('city'),
            data.get('state'),
            data.get('country'),
            data.get('postal_code'),
            data.get('description'),
            data.get('assigned_to')
        ))
        
        company_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return company_id
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.username as assigned_to_name
            FROM companies c
            LEFT JOIN users u ON c.assigned_to = u.id
            ORDER BY c.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_company(self, company_id: int) -> Optional[Dict]:
        """Get company by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM companies WHERE id = ?', (company_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_company(self, company_id: int, data: Dict) -> bool:
        """Update company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        
        for key, value in data.items():
            if key not in ['id', 'created_at']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(company_id)
            query = f"UPDATE companies SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        return True
    
    def delete_company(self, company_id: int) -> bool:
        """Delete company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
        conn.commit()
        conn.close()
        
        return True
    
    # Deal operations
    def add_deal(self, data: Dict) -> int:
        """Add new deal"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO deals (
                title, description, company_id, contact_id, value, stage,
                probability, expected_close_date, owner_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('company_id'),
            data.get('contact_id'),
            data.get('value'),
            data.get('stage', 'lead'),
            data.get('probability', 0),
            data.get('expected_close_date'),
            data.get('owner_id')
        ))
        
        deal_id = cursor.lastrowid
        
        # Log stage change
        cursor.execute('''
            INSERT INTO deal_stage_history (deal_id, to_stage, changed_by)
            VALUES (?, ?, ?)
        ''', (deal_id, data.get('stage', 'lead'), data.get('owner_id')))
        
        conn.commit()
        conn.close()
        
        return deal_id
    
    def get_all_deals(self, status: str = 'open') -> List[Dict]:
        """Get all deals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, 
                   c.name as company_name,
                   ct.name as contact_name,
                   u.username as owner_name
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN customers ct ON d.contact_id = ct.id
            LEFT JOIN users u ON d.owner_id = u.id
            WHERE d.status = ?
            ORDER BY d.created_at DESC
        ''', (status,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_deal(self, deal_id: int, data: Dict, changed_by: int) -> bool:
        """Update deal and track stage changes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current deal to check for stage change
        cursor.execute('SELECT stage FROM deals WHERE id = ?', (deal_id,))
        row = cursor.fetchone()
        old_stage = row['stage'] if row else None
        
        fields = []
        values = []
        
        for key, value in data.items():
            if key not in ['id', 'created_at']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(deal_id)
            query = f"UPDATE deals SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
        
        # If stage changed, log it
        if 'stage' in data and old_stage and data['stage'] != old_stage:
            cursor.execute('''
                INSERT INTO deal_stage_history (deal_id, from_stage, to_stage, changed_by)
                VALUES (?, ?, ?, ?)
            ''', (deal_id, old_stage, data['stage'], changed_by))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_deal(self, deal_id: int) -> Optional[Dict]:
        """Get deal by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, 
                   c.name as company_name,
                   ct.name as contact_name,
                   u.username as owner_name
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN customers ct ON d.contact_id = ct.id
            LEFT JOIN users u ON d.owner_id = u.id
            WHERE d.id = ?
        ''', (deal_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_deals_by_stage(self) -> Dict:
        """Get deals grouped by stage for pipeline view"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, 
                   c.name as company_name,
                   ct.name as contact_name,
                   u.username as owner_name
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN customers ct ON d.contact_id = ct.id
            LEFT JOIN users u ON d.owner_id = u.id
            WHERE d.status = 'open'
            ORDER BY d.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group by stage
        pipeline = {
            'lead': [],
            'qualified': [],
            'proposal': [],
            'negotiation': [],
            'closed_won': [],
            'closed_lost': []
        }
        
        for row in rows:
            deal = dict(row)
            stage = deal.get('stage', 'lead')
            if stage in pipeline:
                pipeline[stage].append(deal)
        
        return pipeline
    
    # Note operations
    def add_note(self, data: Dict) -> int:
        """Add note"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notes (title, content, entity_type, entity_id, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('content'),
            data.get('entity_type'),
            data.get('entity_id'),
            data.get('created_by')
        ))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return note_id
    
    def get_notes(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Get notes for an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.*, u.username as created_by_name
            FROM notes n
            LEFT JOIN users u ON n.created_by = u.id
            WHERE n.entity_type = ? AND n.entity_id = ?
            ORDER BY n.is_pinned DESC, n.created_at DESC
        ''', (entity_type, entity_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Attachment operations
    def add_attachment(self, data: Dict) -> int:
        """Add file attachment"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attachments (
                filename, original_filename, file_path, file_size, mime_type,
                entity_type, entity_id, uploaded_by, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('filename'),
            data.get('original_filename'),
            data.get('file_path'),
            data.get('file_size'),
            data.get('mime_type'),
            data.get('entity_type'),
            data.get('entity_id'),
            data.get('uploaded_by'),
            data.get('description')
        ))
        
        attachment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return attachment_id
    
    def get_attachments(self, entity_type: str, entity_id: int) -> List[Dict]:
        """Get attachments for an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, u.username as uploaded_by_name
            FROM attachments a
            LEFT JOIN users u ON a.uploaded_by = u.id
            WHERE a.entity_type = ? AND a.entity_id = ?
            ORDER BY a.uploaded_at DESC
        ''', (entity_type, entity_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Activity log
    def log_activity(self, user_id: int, action_type: str, entity_type: str, 
                     entity_id: int, description: str, metadata: str = None) -> int:
        """Log user activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO activity_log (
                user_id, action_type, entity_type, entity_id, description, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, action_type, entity_type, entity_id, description, metadata))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_activity_log(self, entity_type: str = None, entity_id: int = None, 
                         limit: int = 50) -> List[Dict]:
        """Get activity log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if entity_type and entity_id:
            cursor.execute('''
                SELECT a.*, u.username
                FROM activity_log a
                LEFT JOIN users u ON a.user_id = u.id
                WHERE a.entity_type = ? AND a.entity_id = ?
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (entity_type, entity_id, limit))
        else:
            cursor.execute('''
                SELECT a.*, u.username
                FROM activity_log a
                LEFT JOIN users u ON a.user_id = u.id
                ORDER BY a.created_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Enhanced task operations
    def get_tasks_by_user(self, user_id: int, status: str = 'pending') -> List[Dict]:
        """Get tasks assigned to a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, 
                   c.name as customer_name,
                   d.title as deal_title,
                   u.username as assigned_by_name
            FROM tasks t
            LEFT JOIN customers c ON t.customer_id = c.id
            LEFT JOIN deals d ON t.related_deal_id = d.id
            LEFT JOIN users u ON t.assigned_by = u.id
            WHERE t.user_id = ? AND t.status = ?
            ORDER BY t.due_date, t.priority DESC
        ''', (user_id, status))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_tasks(self, status: str = None) -> List[Dict]:
        """Get all tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT t.*, 
                       c.name as customer_name,
                       d.title as deal_title,
                       u.username as assigned_to_name,
                       u2.username as assigned_by_name
                FROM tasks t
                LEFT JOIN customers c ON t.customer_id = c.id
                LEFT JOIN deals d ON t.related_deal_id = d.id
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN users u2 ON t.assigned_by = u2.id
                WHERE t.status = ?
                ORDER BY t.due_date, t.priority DESC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT t.*, 
                       c.name as customer_name,
                       d.title as deal_title,
                       u.username as assigned_to_name,
                       u2.username as assigned_by_name
                FROM tasks t
                LEFT JOIN customers c ON t.customer_id = c.id
                LEFT JOIN deals d ON t.related_deal_id = d.id
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN users u2 ON t.assigned_by = u2.id
                ORDER BY t.due_date, t.priority DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
