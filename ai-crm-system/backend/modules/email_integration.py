"""
Email Integration Module - Gmail & Outlook Support
Handles email sync, OAuth authentication, sending emails, and auto-logging interactions
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
import re
import json
from typing import Dict, List, Optional, Any
import sqlite3
from modules import db_helper
from modules.groq_ai import GroqAI

class EmailIntegration:
    """Handle email integration with Gmail and Outlook"""
    
    # Email provider configurations
    PROVIDERS = {
        'gmail': {
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'oauth_scopes': ['https://mail.google.com/'],
            'requires_app_password': True
        },
        'outlook': {
            'imap_server': 'outlook.office365.com',
            'imap_port': 993,
            'smtp_server': 'smtp.office365.com',
            'smtp_port': 587,
            'oauth_scopes': ['https://outlook.office365.com/IMAP.AccessAsUser.All'],
            'requires_app_password': False
        }
    }
    
    def __init__(self):
        self.groq_ai = GroqAI()
        self.db = db_helper.get_db()
        self._create_email_tables()
    
    def _create_email_tables(self):
        """Create tables for email integration"""
        cursor = self.db.cursor()
        
        # Email accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email_address TEXT NOT NULL,
                provider TEXT NOT NULL,
                display_name TEXT,
                is_primary BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                auth_type TEXT DEFAULT 'password',
                encrypted_password TEXT,
                oauth_token TEXT,
                oauth_refresh_token TEXT,
                token_expiry TIMESTAMP,
                last_sync TIMESTAMP,
                sync_enabled BOOLEAN DEFAULT 1,
                auto_log_interactions BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, email_address)
            )
        """)
        
        # Email sync log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                message_id TEXT NOT NULL,
                subject TEXT,
                from_email TEXT,
                to_email TEXT,
                cc_email TEXT,
                sent_date TIMESTAMP,
                body_preview TEXT,
                has_attachments BOOLEAN DEFAULT 0,
                is_read BOOLEAN DEFAULT 0,
                is_sent BOOLEAN DEFAULT 0,
                folder TEXT DEFAULT 'INBOX',
                interaction_id INTEGER,
                customer_id INTEGER,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, message_id),
                FOREIGN KEY (account_id) REFERENCES email_accounts(id),
                FOREIGN KEY (interaction_id) REFERENCES interactions(id),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        
        # Email templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                variables TEXT,
                is_shared BOOLEAN DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db.commit()
    
    def add_email_account(self, user_id: int, email_address: str, provider: str, 
                         password: str = None, display_name: str = None) -> Dict[str, Any]:
        """Add a new email account for sync"""
        try:
            if provider not in self.PROVIDERS:
                return {
                    'success': False,
                    'error': f'Unsupported provider: {provider}. Use gmail or outlook.'
                }
            
            cursor = self.db.cursor()
            
            # Check if account already exists
            cursor.execute("""
                SELECT id FROM email_accounts 
                WHERE user_id = ? AND email_address = ?
            """, (user_id, email_address))
            
            existing = cursor.fetchone()
            if existing:
                return {
                    'success': False,
                    'error': 'Email account already added',
                    'account_id': existing[0]
                }
            
            # Test connection before adding
            if password:
                test_result = self._test_connection(email_address, password, provider)
                if not test_result['success']:
                    return {
                        'success': False,
                        'error': f'Failed to connect: {test_result.get("error")}'
                    }
            
            # Encrypt password (in production, use proper encryption)
            encrypted_pwd = self._encrypt_password(password) if password else None
            
            # Insert account
            cursor.execute("""
                INSERT INTO email_accounts 
                (user_id, email_address, provider, display_name, encrypted_password, auth_type)
                VALUES (?, ?, ?, ?, ?, 'password')
            """, (user_id, email_address, provider, display_name or email_address, encrypted_pwd))
            
            account_id = cursor.lastrowid
            self.db.commit()
            
            return {
                'success': True,
                'account_id': account_id,
                'message': f'Email account {email_address} added successfully'
            }
            
        except Exception as e:
            print(f"Error adding email account: {e}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def _test_connection(self, email_address: str, password: str, provider: str) -> Dict[str, Any]:
        """Test IMAP connection"""
        try:
            config = self.PROVIDERS[provider]
            
            # Test IMAP connection
            mail = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
            mail.login(email_address, password)
            mail.logout()
            
            return {'success': True}
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def sync_emails(self, account_id: int, days_back: int = 7, 
                   auto_log: bool = True) -> Dict[str, Any]:
        """Sync emails from email provider"""
        try:
            cursor = self.db.cursor()
            
            # Get account details
            cursor.execute("""
                SELECT email_address, provider, encrypted_password, last_sync
                FROM email_accounts WHERE id = ?
            """, (account_id,))
            
            account = cursor.fetchone()
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            email_address, provider, encrypted_pwd, last_sync = account
            password = self._decrypt_password(encrypted_pwd)
            
            if not password:
                return {'success': False, 'error': 'No password configured'}
            
            config = self.PROVIDERS[provider]
            
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(config['imap_server'], config['imap_port'])
            mail.login(email_address, password)
            mail.select('INBOX')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%d-%b-%Y')
            
            # Search for emails
            _, message_numbers = mail.search(None, f'SINCE {since_date}')
            
            synced_count = 0
            logged_count = 0
            
            for num in message_numbers[0].split()[-50:]:  # Limit to 50 most recent
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Extract email details
                message_id = email_message.get('Message-ID', '')
                subject = self._decode_header(email_message.get('Subject', ''))
                from_email = self._extract_email(email_message.get('From', ''))
                to_email = self._extract_email(email_message.get('To', ''))
                cc_email = self._extract_email(email_message.get('Cc', ''))
                sent_date = email_message.get('Date', '')
                
                # Get email body
                body_preview = self._get_email_body(email_message)[:500]
                
                # Check if already synced
                cursor.execute("""
                    SELECT id FROM email_sync_log 
                    WHERE account_id = ? AND message_id = ?
                """, (account_id, message_id))
                
                if cursor.fetchone():
                    continue
                
                # Parse date
                try:
                    sent_datetime = email.utils.parsedate_to_datetime(sent_date)
                except:
                    sent_datetime = datetime.now()
                
                # Find matching customer
                customer_id = self._find_customer_by_email(from_email if from_email != email_address else to_email)
                
                # Insert into sync log
                cursor.execute("""
                    INSERT INTO email_sync_log 
                    (account_id, message_id, subject, from_email, to_email, cc_email,
                     sent_date, body_preview, is_sent, customer_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    account_id, message_id, subject, from_email, to_email, cc_email,
                    sent_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    body_preview,
                    1 if from_email == email_address else 0,
                    customer_id
                ))
                
                email_log_id = cursor.lastrowid
                synced_count += 1
                
                # Auto-log as interaction if enabled
                if auto_log and customer_id:
                    interaction_id = self._log_email_interaction(
                        customer_id, subject, body_preview, 
                        sent_datetime, from_email == email_address
                    )
                    
                    if interaction_id:
                        cursor.execute("""
                            UPDATE email_sync_log 
                            SET interaction_id = ? 
                            WHERE id = ?
                        """, (interaction_id, email_log_id))
                        logged_count += 1
            
            # Update last sync time
            cursor.execute("""
                UPDATE email_accounts 
                SET last_sync = ? 
                WHERE id = ?
            """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), account_id))
            
            self.db.commit()
            mail.logout()
            
            return {
                'success': True,
                'synced': synced_count,
                'logged_interactions': logged_count,
                'message': f'Synced {synced_count} emails, logged {logged_count} interactions'
            }
            
        except Exception as e:
            print(f"Error syncing emails: {e}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_email(self, account_id: int, to_email: str, subject: str, 
                  body: str, customer_id: Optional[int] = None,
                  cc: Optional[str] = None, template_id: Optional[int] = None) -> Dict[str, Any]:
        """Send email through configured account"""
        try:
            cursor = self.db.cursor()
            
            # Get account details
            cursor.execute("""
                SELECT email_address, provider, encrypted_password, display_name
                FROM email_accounts WHERE id = ?
            """, (account_id,))
            
            account = cursor.fetchone()
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            email_address, provider, encrypted_pwd, display_name = account
            password = self._decrypt_password(encrypted_pwd)
            
            config = self.PROVIDERS[provider]
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{display_name} <{email_address}>" if display_name else email_address
            msg['To'] = to_email
            msg['Subject'] = subject
            if cc:
                msg['Cc'] = cc
            
            # Add body
            html_body = self._convert_to_html(body)
            msg.attach(MIMEText(body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(email_address, password)
            
            recipients = [to_email]
            if cc:
                recipients.extend(cc.split(','))
            
            server.send_message(msg, email_address, recipients)
            server.quit()
            
            # Log to email_sync_log
            cursor.execute("""
                INSERT INTO email_sync_log 
                (account_id, message_id, subject, from_email, to_email, cc_email,
                 sent_date, body_preview, is_sent, customer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                account_id,
                f"<sent-{datetime.now().timestamp()}@crm>",
                subject,
                email_address,
                to_email,
                cc,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                body[:500],
                customer_id
            ))
            
            email_log_id = cursor.lastrowid
            
            # Auto-log as interaction
            if customer_id:
                interaction_id = self._log_email_interaction(
                    customer_id, subject, body, datetime.now(), is_sent=True
                )
                
                cursor.execute("""
                    UPDATE email_sync_log 
                    SET interaction_id = ? 
                    WHERE id = ?
                """, (interaction_id, email_log_id))
            
            # Update template usage
            if template_id:
                cursor.execute("""
                    UPDATE email_templates 
                    SET usage_count = usage_count + 1 
                    WHERE id = ?
                """, (template_id,))
            
            self.db.commit()
            
            return {
                'success': True,
                'message': f'Email sent to {to_email}',
                'email_log_id': email_log_id
            }
            
        except Exception as e:
            print(f"Error sending email: {e}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def save_template(self, user_id: int, name: str, subject: str, body: str,
                     category: str = 'general', variables: List[str] = None) -> Dict[str, Any]:
        """Save an email template"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                INSERT INTO email_templates 
                (user_id, name, subject, body, category, variables)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id, name, subject, body, category,
                json.dumps(variables or [])
            ))
            
            template_id = cursor.lastrowid
            self.db.commit()
            
            return {
                'success': True,
                'template_id': template_id,
                'message': f'Template "{name}" saved successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_templates(self, user_id: int, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get email templates"""
        try:
            cursor = self.db.cursor()
            
            query = """
                SELECT id, name, subject, body, category, variables, usage_count, created_at
                FROM email_templates
                WHERE user_id = ? OR is_shared = 1
            """
            params = [user_id]
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            query += " ORDER BY usage_count DESC, created_at DESC"
            
            cursor.execute(query, params)
            
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'id': row[0],
                    'name': row[1],
                    'subject': row[2],
                    'body': row[3],
                    'category': row[4],
                    'variables': json.loads(row[5]) if row[5] else [],
                    'usage_count': row[6],
                    'created_at': row[7]
                })
            
            return templates
            
        except Exception as e:
            print(f"Error getting templates: {e}")
            return []
    
    def apply_template(self, template_id: int, variables: Dict[str, str]) -> Dict[str, Any]:
        """Apply variables to a template"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                SELECT subject, body FROM email_templates WHERE id = ?
            """, (template_id,))
            
            template = cursor.fetchone()
            if not template:
                return {'success': False, 'error': 'Template not found'}
            
            subject, body = template
            
            # Replace variables
            for key, value in variables.items():
                subject = subject.replace(f'{{{{{key}}}}}', str(value))
                body = body.replace(f'{{{{{key}}}}}', str(value))
            
            return {
                'success': True,
                'subject': subject,
                'body': body
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_email_interaction(self, customer_id: int, subject: str, body: str,
                               sent_date: datetime, is_sent: bool) -> Optional[int]:
        """Log email as CRM interaction"""
        try:
            cursor = self.db.cursor()
            
            notes = f"Subject: {subject}\n\n{body[:1000]}"
            interaction_type = 'email_sent' if is_sent else 'email_received'
            
            cursor.execute("""
                INSERT INTO interactions 
                (customer_id, type, notes, created_at, channel)
                VALUES (?, ?, ?, ?, 'email')
            """, (
                customer_id,
                'email',
                notes,
                sent_date.strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            interaction_id = cursor.lastrowid
            self.db.commit()
            
            return interaction_id
            
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return None
    
    def _find_customer_by_email(self, email_address: str) -> Optional[int]:
        """Find customer by email address"""
        if not email_address:
            return None
        
        try:
            cursor = self.db.cursor()
            
            # Try direct match
            cursor.execute("""
                SELECT id FROM customers WHERE email = ? LIMIT 1
            """, (email_address,))
            
            customer = cursor.fetchone()
            if customer:
                return customer[0]
            
            # Try contacts table
            cursor.execute("""
                SELECT customer_id FROM contacts WHERE email = ? LIMIT 1
            """, (email_address,))
            
            contact = cursor.fetchone()
            if contact:
                return contact[0]
            
            return None
            
        except Exception as e:
            print(f"Error finding customer: {e}")
            return None
    
    def _extract_email(self, email_str: str) -> str:
        """Extract email address from email string"""
        if not email_str:
            return ''
        
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email_str)
        return match.group(0) if match else email_str
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ''
        
        decoded = decode_header(header)
        result = ''
        
        for part, encoding in decoded:
            if isinstance(part, bytes):
                result += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                result += part
        
        return result
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body"""
        body = ''
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body.strip()
    
    def _convert_to_html(self, text: str) -> str:
        """Convert plain text to HTML"""
        html = text.replace('\n', '<br>')
        return f'<html><body>{html}</body></html>'
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt password (simple base64 for demo - use proper encryption in production)"""
        import base64
        return base64.b64encode(password.encode()).decode()
    
    def _decrypt_password(self, encrypted: str) -> str:
        """Decrypt password"""
        if not encrypted:
            return ''
        import base64
        return base64.b64decode(encrypted.encode()).decode()
