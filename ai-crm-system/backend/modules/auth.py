# modules/auth.py
"""
Authentication Module - User authentication and authorization
"""

from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from typing import Dict, Optional
import secrets
import string
from datetime import datetime, timedelta

class Auth:
    def __init__(self, db_path='crm_database.db'):
        """Initialize authentication system"""
        self.db_path = db_path
        self.session_timeout = timedelta(hours=8)
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        
        return None
    
    def create_user(self, username: str, password: str, email: str, role: str = 'user') -> bool:
        """Create new user account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = generate_password_hash(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, role))
            
            conn.commit()
            conn.close()
            
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = generate_password_hash(new_password)
            
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (password_hash, user_id))
            
            conn.commit()
            conn.close()
            
            return True
        except:
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user account"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except:
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_all_users(self) -> list:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, role FROM users')
        users = cursor.fetchall()
        
        conn.close()
        
        return [dict(user) for user in users]
    
    def update_user_role(self, user_id: int, new_role: str) -> bool:
        """Update user role"""
        valid_roles = ['admin', 'manager', 'user', 'viewer']
        
        if new_role not in valid_roles:
            return False
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET role = ? WHERE id = ?
            ''', (new_role, user_id))
            
            conn.commit()
            conn.close()
            
            return True
        except:
            return False
    
    def generate_token(self, length: int = 32) -> str:
        """Generate secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        permissions = {
            'admin': ['all', 'read', 'write', 'delete', 'manage_users', 'manage_team', 'view_reports', 'export_data'],
            'manager': ['read', 'write', 'delete', 'manage_team', 'view_reports', 'export_data'],
            'user': ['read', 'write', 'view_own_data'],
            'viewer': ['read', 'view_own_data']
        }
        
        if user_role == 'admin':
            return True
        
        user_permissions = permissions.get(user_role, [])
        return required_permission in user_permissions
    
    def validate_password_strength(self, password: str) -> Dict:
        """Validate password strength"""
        result = {
            'is_valid': True,
            'errors': [],
            'strength': 'weak'
        }
        
        # Check length
        if len(password) < 8:
            result['is_valid'] = False
            result['errors'].append('Password must be at least 8 characters long')
        
        # Check for uppercase
        if not any(c.isupper() for c in password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one uppercase letter')
        
        # Check for lowercase
        if not any(c.islower() for c in password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one lowercase letter')
        
        # Check for digits
        if not any(c.isdigit() for c in password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one number')
        
        # Check for special characters
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        if not any(c in special_chars for c in password):
            result['is_valid'] = False
            result['errors'].append('Password must contain at least one special character')
        
        # Determine strength
        if result['is_valid']:
            if len(password) >= 12 and any(c in special_chars for c in password):
                result['strength'] = 'strong'
            elif len(password) >= 10:
                result['strength'] = 'medium'
            else:
                result['strength'] = 'weak'
        
        return result
    
    def create_default_users(self):
        """Create default users for testing"""
        default_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@crm.com',
                'role': 'admin'
            },
            {
                'username': 'manager',
                'password': 'manager123',
                'email': 'manager@crm.com',
                'role': 'manager'
            },
            {
                'username': 'user',
                'password': 'user123',
                'email': 'user@crm.com',
                'role': 'user'
            }
        ]
        
        for user in default_users:
            self.create_user(
                username=user['username'],
                password=user['password'],
                email=user['email'],
                role=user['role']
            )
    
    def reset_password_request(self, email: str) -> Optional[str]:
        """Generate password reset token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        conn.close()
        
        if user:
            # Generate reset token
            token = self.generate_token(48)
            
            # In production, you would store this token in a separate table
            # with an expiration time and send it via email
            return token
        
        return None
    
    def verify_reset_token(self, token: str) -> bool:
        """Verify password reset token"""
        # In production, this would check the token against the database
        # and verify it hasn't expired
        return len(token) == 48  # Simple validation for demo
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get active sessions for a user"""
        # In production, this would track actual sessions
        return [
            {
                'id': 'session_1',
                'created_at': datetime.now() - timedelta(hours=2),
                'last_activity': datetime.now() - timedelta(minutes=5),
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0...'
            }
        ]
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke a specific session"""
        # In production, this would invalidate the session
        return True
    
    def revoke_all_sessions(self, user_id: int) -> bool:
        """Revoke all sessions for a user"""
        # In production, this would invalidate all user sessions
        return True