# modules/database.py
"""
Database Module - Handles all database operations for the CRM
Uses SQLite for simplicity and portability
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class Database:
    def __init__(self, db_path='crm_database.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        """Create necessary database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                company TEXT,
                industry TEXT,
                status TEXT DEFAULT 'lead',
                lead_score REAL DEFAULT 0,
                budget REAL,
                location TEXT,
                website TEXT,
                notes TEXT,
                assigned_to INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_to) REFERENCES users(id)
            )
        ''')
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                user_id INTEGER,
                type TEXT NOT NULL,
                channel TEXT,
                subject TEXT,
                notes TEXT,
                outcome TEXT,
                next_action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Sales opportunities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                value REAL,
                probability REAL,
                stage TEXT DEFAULT 'prospecting',
                expected_close_date DATE,
                actual_close_date DATE,
                status TEXT DEFAULT 'open',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        # Tasks/Reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                user_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                due_date TIMESTAMP,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                type TEXT DEFAULT 'follow-up',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # AI Insights cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                insight_type TEXT,
                content TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Customer operations
    def add_customer(self, data: Dict) -> int:
        """Add new customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO customers (name, email, phone, company, industry, status, budget, location, website, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('company'),
            data.get('industry'),
            data.get('status', 'lead'),
            data.get('budget', 0),
            data.get('location'),
            data.get('website'),
            data.get('notes')
        ))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return customer_id
    
    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_all_customers(self) -> List[Dict]:
        """Get all customers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_customer(self, customer_id: int, data: Dict):
        """Update customer information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        
        for key, value in data.items():
            if key not in ['id', 'created_at']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        values.append(datetime.now())
        values.append(customer_id)
        
        query = f'''
            UPDATE customers 
            SET {', '.join(fields)}, updated_at = ?
            WHERE id = ?
        '''
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def update_customer_score(self, customer_id: int, score: float):
        """Update customer lead score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE customers 
            SET lead_score = ?, updated_at = ?
            WHERE id = ?
        ''', (score, datetime.now(), customer_id))
        
        conn.commit()
        conn.close()
    
    def delete_customer(self, customer_id: int):
        """Delete customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete related records first
        cursor.execute('DELETE FROM interactions WHERE customer_id = ?', (customer_id,))
        cursor.execute('DELETE FROM opportunities WHERE customer_id = ?', (customer_id,))
        cursor.execute('DELETE FROM tasks WHERE customer_id = ?', (customer_id,))
        cursor.execute('DELETE FROM ai_insights WHERE customer_id = ?', (customer_id,))
        
        # Delete customer
        cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # Interaction operations
    def add_interaction(self, data: Dict) -> int:
        """Add customer interaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (customer_id, user_id, type, channel, subject, notes, outcome, next_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('customer_id'),
            data.get('user_id'),
            data.get('type'),
            data.get('channel'),
            data.get('subject'),
            data.get('notes'),
            data.get('outcome'),
            data.get('next_action')
        ))
        
        interaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return interaction_id
    
    def get_customer_interactions(self, customer_id: int) -> List[Dict]:
        """Get all interactions for a customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, u.username 
            FROM interactions i
            LEFT JOIN users u ON i.user_id = u.id
            WHERE i.customer_id = ?
            ORDER BY i.created_at DESC
        ''', (customer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_all_interactions(self) -> List[Dict]:
        """Get all interactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, c.name as customer_name, u.username 
            FROM interactions i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, c.name as customer_name, u.username 
            FROM interactions i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Analytics operations
    def get_customer_count(self) -> int:
        """Get total customer count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM customers')
        result = cursor.fetchone()
        
        conn.close()
        
        return result['count']
    
    def get_active_leads_count(self) -> int:
        """Get active leads count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM customers WHERE status IN (?, ?)', ('lead', 'qualified'))
        result = cursor.fetchone()
        
        conn.close()
        
        return result['count']
    
    def get_conversion_rate(self) -> float:
        """Calculate conversion rate"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total FROM customers')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as converted FROM customers WHERE status = ?', ('customer',))
        converted = cursor.fetchone()['converted']
        
        conn.close()
        
        if total > 0:
            return round((converted / total) * 100, 2)
        return 0
    
    def get_monthly_revenue(self) -> float:
        """Get monthly revenue from opportunities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        cursor.execute('''
            SELECT SUM(value) as revenue 
            FROM opportunities 
            WHERE status = ? AND actual_close_date >= ?
        ''', ('won', thirty_days_ago))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['revenue'] if result['revenue'] else 0
    
    def get_top_leads(self, limit: int = 5) -> List[Dict]:
        """Get top leads by score"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM customers 
            WHERE status IN (?, ?)
            ORDER BY lead_score DESC
            LIMIT ?
        ''', ('lead', 'qualified', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Opportunity operations
    def add_opportunity(self, data: Dict) -> int:
        """Add sales opportunity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opportunities (customer_id, title, value, probability, stage, expected_close_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('customer_id'),
            data.get('title'),
            data.get('value'),
            data.get('probability'),
            data.get('stage', 'prospecting'),
            data.get('expected_close_date'),
            data.get('notes')
        ))
        
        opportunity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return opportunity_id
    
    def get_opportunities(self, status: str = 'open') -> List[Dict]:
        """Get opportunities by status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT o.*, c.name as customer_name 
            FROM opportunities o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.status = ?
            ORDER BY o.expected_close_date
        ''', (status,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # Task operations
    def add_task(self, data: Dict) -> int:
        """Add task/reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (customer_id, user_id, title, description, due_date, priority, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('customer_id'),
            data.get('user_id'),
            data.get('title'),
            data.get('description'),
            data.get('due_date'),
            data.get('priority', 'medium'),
            data.get('type', 'follow-up')
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_user_tasks(self, user_id: int, status: str = 'pending') -> List[Dict]:
        """Get tasks for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, c.name as customer_name 
            FROM tasks t
            LEFT JOIN customers c ON t.customer_id = c.id
            WHERE t.user_id = ? AND t.status = ?
            ORDER BY t.due_date
        ''', (user_id, status))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]