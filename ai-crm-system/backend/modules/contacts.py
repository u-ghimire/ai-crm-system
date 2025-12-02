"""
Contacts API Module
Manages contacts (people) with company relationships
Industry-standard CRM architecture: Company → Contacts → Deals
"""

from flask import Blueprint, request, jsonify, session
from .db_helper import get_db
from functools import wraps
from datetime import datetime

contacts_bp = Blueprint('contacts', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@contacts_bp.route('/api/contacts', methods=['GET'])
@login_required
def get_contacts():
    """
    Get all contacts with optional filtering
    Query params: company_id, status, search, assigned_to
    """
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters
        company_id = request.args.get('company_id', type=int)
        status = request.args.get('status', '')
        search = request.args.get('search', '')
        assigned_to = request.args.get('assigned_to', type=int)
        
        # Build query
        query = '''
            SELECT 
                c.id, c.first_name, c.last_name,
                c.email, c.phone, c.mobile_phone,
                c.job_title, c.department, c.role,
                c.company_id, c.linkedin_url, c.twitter_url,
                c.status, c.lead_score, c.source,
                c.assigned_to, c.location, c.country,
                c.notes, c.tags, c.created_at, c.updated_at,
                c.last_contacted_at,
                co.name as company_name,
                co.industry as company_industry,
                co.website as company_website,
                u.username as assigned_to_name
            FROM contacts c
            LEFT JOIN companies co ON c.company_id = co.id
            LEFT JOIN users u ON c.assigned_to = u.id
            WHERE 1=1
        '''
        params = []
        
        if company_id:
            query += " AND c.company_id = ?"
            params.append(company_id)
        
        if status:
            query += " AND c.status = ?"
            params.append(status)
        
        if search:
            query += " AND (c.first_name LIKE ? OR c.last_name LIKE ? OR c.email LIKE ? OR co.name LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if assigned_to:
            query += " AND c.assigned_to = ?"
            params.append(assigned_to)
        
        query += " ORDER BY c.last_name, c.first_name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        contacts = []
        for row in rows:
            contacts.append({
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'full_name': f"{row[1]} {row[2]}",
                'email': row[3],
                'phone': row[4],
                'mobile_phone': row[5],
                'job_title': row[6],
                'department': row[7],
                'role': row[8],
                'company_id': row[9],
                'linkedin_url': row[10],
                'twitter_url': row[11],
                'status': row[12],
                'lead_score': row[13],
                'source': row[14],
                'assigned_to': row[15],
                'location': row[16],
                'country': row[17],
                'notes': row[18],
                'tags': row[19],
                'created_at': row[20],
                'updated_at': row[21],
                'last_contacted_at': row[22],
                'company_name': row[23],
                'company_industry': row[24],
                'company_website': row[25],
                'assigned_to_name': row[26]
            })
        
        return jsonify({'success': True, 'contacts': contacts})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['GET'])
@login_required
def get_contact(contact_id):
    """Get a single contact with full details including related deals"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get contact details
        cursor.execute('''
            SELECT 
                c.id, c.first_name, c.last_name,
                c.email, c.phone, c.mobile_phone,
                c.job_title, c.department, c.role,
                c.company_id, c.linkedin_url, c.twitter_url,
                c.status, c.lead_score, c.source,
                c.assigned_to, c.location, c.country,
                c.notes, c.tags, c.created_at, c.updated_at,
                c.last_contacted_at,
                co.name as company_name,
                co.industry as company_industry,
                co.website as company_website,
                u.username as assigned_to_name
            FROM contacts c
            LEFT JOIN companies co ON c.company_id = co.id
            LEFT JOIN users u ON c.assigned_to = u.id
            WHERE c.id = ?
        ''', (contact_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Contact not found'}), 404
        
        contact = {
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'full_name': f"{row[1]} {row[2]}",
            'email': row[3],
            'phone': row[4],
            'mobile_phone': row[5],
            'job_title': row[6],
            'department': row[7],
            'role': row[8],
            'company_id': row[9],
            'linkedin_url': row[10],
            'twitter_url': row[11],
            'status': row[12],
            'lead_score': row[13],
            'source': row[14],
            'assigned_to': row[15],
            'location': row[16],
            'country': row[17],
            'notes': row[18],
            'tags': row[19],
            'created_at': row[20],
            'updated_at': row[21],
            'last_contacted_at': row[22],
            'company_name': row[23],
            'company_industry': row[24],
            'company_website': row[25],
            'assigned_to_name': row[26]
        }
        
        # Get related deals
        cursor.execute('''
            SELECT d.id, d.title, d.deal_number, d.value, d.stage, d.status,
                   dc.role, dc.is_primary
            FROM deal_contacts dc
            JOIN deals d ON dc.deal_id = d.id
            WHERE dc.contact_id = ?
            ORDER BY dc.is_primary DESC, d.created_at DESC
        ''', (contact_id,))
        
        deals = []
        for deal_row in cursor.fetchall():
            deals.append({
                'id': deal_row[0],
                'title': deal_row[1],
                'deal_number': deal_row[2],
                'value': deal_row[3],
                'stage': deal_row[4],
                'status': deal_row[5],
                'role': deal_row[6],
                'is_primary': bool(deal_row[7])
            })
        
        contact['deals'] = deals
        
        return jsonify({'success': True, 'contact': contact})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts', methods=['POST'])
@login_required
def create_contact():
    """Create a new contact"""
    db = None
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('first_name'):
            return jsonify({'success': False, 'message': 'First name is required'}), 400
        if not data.get('last_name'):
            return jsonify({'success': False, 'message': 'Last name is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (
                first_name, last_name, email, phone, mobile_phone,
                job_title, department, role, company_id,
                linkedin_url, twitter_url, personal_website,
                status, lead_score, source, assigned_to,
                timezone, location, country, notes, tags, custom_fields
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone'),
            data.get('mobile_phone'),
            data.get('job_title'),
            data.get('department'),
            data.get('role'),
            data.get('company_id'),
            data.get('linkedin_url'),
            data.get('twitter_url'),
            data.get('personal_website'),
            data.get('status', 'lead'),
            data.get('lead_score', 0),
            data.get('source'),
            data.get('assigned_to', session['user_id']),
            data.get('timezone'),
            data.get('location'),
            data.get('country'),
            data.get('notes'),
            data.get('tags'),
            data.get('custom_fields')
        ))
        
        contact_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contact created successfully',
            'contact_id': contact_id
        }), 201
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['PUT'])
@login_required
def update_contact(contact_id):
    """Update an existing contact"""
    db = None
    try:
        data = request.json
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE contacts SET
                first_name = ?,
                last_name = ?,
                email = ?,
                phone = ?,
                mobile_phone = ?,
                job_title = ?,
                department = ?,
                role = ?,
                company_id = ?,
                linkedin_url = ?,
                twitter_url = ?,
                personal_website = ?,
                status = ?,
                lead_score = ?,
                source = ?,
                assigned_to = ?,
                timezone = ?,
                location = ?,
                country = ?,
                notes = ?,
                tags = ?,
                custom_fields = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone'),
            data.get('mobile_phone'),
            data.get('job_title'),
            data.get('department'),
            data.get('role'),
            data.get('company_id'),
            data.get('linkedin_url'),
            data.get('twitter_url'),
            data.get('personal_website'),
            data.get('status'),
            data.get('lead_score'),
            data.get('source'),
            data.get('assigned_to'),
            data.get('timezone'),
            data.get('location'),
            data.get('country'),
            data.get('notes'),
            data.get('tags'),
            data.get('custom_fields'),
            contact_id
        ))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contact updated successfully'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    """Delete a contact"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if contact has deals
        cursor.execute('SELECT COUNT(*) FROM deal_contacts WHERE contact_id = ?', (contact_id,))
        deal_count = cursor.fetchone()[0]
        
        if deal_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete contact with {deal_count} associated deal(s). Remove from deals first.'
            }), 400
        
        cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contact deleted successfully'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/<int:contact_id>/deals', methods=['GET'])
@login_required
def get_contact_deals(contact_id):
    """Get all deals associated with a contact"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT 
                d.id, d.title, d.deal_number, d.company_id, d.value,
                d.stage, d.status, d.expected_close_date,
                dc.role, dc.is_primary,
                co.name as company_name
            FROM deal_contacts dc
            JOIN deals d ON dc.deal_id = d.id
            LEFT JOIN companies co ON d.company_id = co.id
            WHERE dc.contact_id = ?
            ORDER BY dc.is_primary DESC, d.created_at DESC
        ''', (contact_id,))
        
        deals = []
        for row in cursor.fetchall():
            deals.append({
                'id': row[0],
                'title': row[1],
                'deal_number': row[2],
                'company_id': row[3],
                'value': row[4],
                'stage': row[5],
                'status': row[6],
                'expected_close_date': row[7],
                'role': row[8],
                'is_primary': bool(row[9]),
                'company_name': row[10]
            })
        
        return jsonify({'success': True, 'deals': deals})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/<int:contact_id>/touch', methods=['POST'])
@login_required
def touch_contact(contact_id):
    """Update last_contacted_at timestamp"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE contacts 
            SET last_contacted_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (contact_id,))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Contact touch timestamp updated'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@contacts_bp.route('/api/contacts/stats', methods=['GET'])
@login_required
def get_contact_stats():
    """Get contact statistics"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        user_id = session['user_id']
        
        # Total contacts
        cursor.execute('SELECT COUNT(*) FROM contacts WHERE assigned_to = ?', (user_id,))
        total = cursor.fetchone()[0]
        
        # By status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM contacts
            WHERE assigned_to = ?
            GROUP BY status
        ''', (user_id,))
        
        by_status = {}
        for row in cursor.fetchall():
            by_status[row[0]] = row[1]
        
        # Contacts without company
        cursor.execute('SELECT COUNT(*) FROM contacts WHERE assigned_to = ? AND company_id IS NULL', (user_id,))
        without_company = cursor.fetchone()[0]
        
        # Recent contacts (last 30 days)
        cursor.execute('''
            SELECT COUNT(*) FROM contacts 
            WHERE assigned_to = ? 
            AND created_at >= date('now', '-30 days')
        ''', (user_id,))
        recent = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'by_status': by_status,
                'without_company': without_company,
                'recent_30_days': recent
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()
