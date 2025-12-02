"""
Enhanced Deals/Pipeline Management Module
Handles deal/opportunity CRUD and pipeline operations
"""

from flask import Blueprint, request, jsonify, session
from .db_helper import get_db
from functools import wraps
from datetime import datetime

deals_bp = Blueprint('deals', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@deals_bp.route('/api/deals', methods=['GET'])
@login_required
def get_deals():
    """Get all deals with filtering and pipeline view"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters
        stage = request.args.get('stage', '')
        company_id = request.args.get('company_id', type=int)
        contact_id = request.args.get('contact_id', type=int)
        
        query = '''
            SELECT d.*, 
                   c.name as company_name,
                   con.first_name || ' ' || con.last_name as primary_contact_name,
                   con.email as primary_contact_email,
                   con.phone as primary_contact_phone
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN contacts con ON d.primary_contact_id = con.id
            WHERE 1=1
        '''
        params = []
        
        if stage:
            query += ' AND d.stage = ?'
            params.append(stage)
        
        if company_id:
            query += ' AND d.company_id = ?'
            params.append(company_id)
        
        if contact_id:
            query += ' AND d.primary_contact_id = ?'
            params.append(contact_id)
        
        query += ' ORDER BY d.created_at DESC'
        
        cursor.execute(query, params)
        deals = []
        for row in cursor.fetchall():
            deal_dict = dict(row)
            deal_id = deal_dict['id']
            
            # Get all involved contacts
            cursor.execute('''
                SELECT con.id, con.first_name, con.last_name, con.email, dc.role
                FROM deal_contacts dc
                JOIN contacts con ON dc.contact_id = con.id
                WHERE dc.deal_id = ?
            ''', (deal_id,))
            
            deal_dict['contacts'] = [dict(c) for c in cursor.fetchall()]
            deals.append(deal_dict)
        
        return jsonify({'success': True, 'deals': deals})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals/pipeline', methods=['GET'])
@login_required
def get_pipeline():
    """Get pipeline view grouped by stages"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get all deal stages
        cursor.execute('''
            SELECT name, order_index, probability
            FROM deal_stages
            WHERE is_active = 1
            ORDER BY order_index
        ''')
        
        stages = []
        for row in cursor.fetchall():
            stage_name = row[0]
            
            # Get deals for this stage
            cursor.execute('''
                SELECT d.id, d.title, d.value, d.probability,
                       d.expected_close_date, c.name as company_name,
                       con.first_name || ' ' || con.last_name as primary_contact_name
                FROM deals d
                LEFT JOIN companies c ON d.company_id = c.id
                LEFT JOIN contacts con ON d.primary_contact_id = con.id
                WHERE d.stage = ?
                ORDER BY d.created_at DESC
            ''', (stage_name,))
            
            deals = []
            total_value = 0
            for deal_row in cursor.fetchall():
                deal_value = deal_row[2] or 0
                total_value += deal_value
                
                deal_dict = {
                    'id': deal_row[0],
                    'name': deal_row[1],
                    'title': deal_row[1],
                    'value': deal_value,
                    'probability': deal_row[3],
                    'expected_close_date': deal_row[4],
                    'company_name': deal_row[5],
                    'primary_contact_name': deal_row[6]
                }
                
                # Get all involved contacts for this deal
                cursor.execute('''
                    SELECT con.first_name || ' ' || con.last_name as name, dc.role
                    FROM deal_contacts dc
                    JOIN contacts con ON dc.contact_id = con.id
                    WHERE dc.deal_id = ?
                ''', (deal_row[0],))
                deal_dict['contacts'] = [dict(c) for c in cursor.fetchall()]
                
                deals.append(deal_dict)
            
            stages.append({
                'name': stage_name,
                'order_index': row[1],
                'default_probability': row[2],
                'deals': deals,
                'deal_count': len(deals),
                'total_value': total_value
            })
        
        return jsonify({'success': True, 'pipeline': stages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals/<int:deal_id>', methods=['GET'])
@login_required
def get_deal(deal_id):
    """Get a specific deal with details"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT d.*, 
                   c.name as company_name,
                   con.first_name || ' ' || con.last_name as primary_contact_name,
                   con.email as primary_contact_email,
                   con.phone as primary_contact_phone
            FROM deals d
            LEFT JOIN companies c ON d.company_id = c.id
            LEFT JOIN contacts con ON d.primary_contact_id = con.id
            WHERE d.id = ?
        ''', (deal_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Deal not found'}), 404
        
        deal = dict(row)
        
        # Get all involved contacts
        cursor.execute('''
            SELECT con.*, dc.role, dc.is_primary
            FROM deal_contacts dc
            JOIN contacts con ON dc.contact_id = con.id
            WHERE dc.deal_id = ?
            ORDER BY dc.is_primary DESC, con.first_name
        ''', (deal_id,))
        
        deal['contacts'] = [dict(c) for c in cursor.fetchall()]
        
        # Get associated activities
        cursor.execute('''
            SELECT id, activity_type, subject, activity_date, outcome
            FROM activities
            WHERE deal_id = ?
            ORDER BY activity_date DESC
            LIMIT 10
        ''', (deal_id,))
        
        deal['activities'] = [dict(a) for a in cursor.fetchall()]
        
        return jsonify({'success': True, 'deal': deal})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals', methods=['POST'])
@login_required
def create_deal():
    """Create a new deal"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('company_id'):
            return jsonify({'success': False, 'message': 'company_id is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Generate deal number
        cursor.execute('SELECT COUNT(*) as count FROM deals')
        count = cursor.fetchone()['count']
        deal_number = f"DEAL-{count + 1:05d}"
        
        cursor.execute('''
            INSERT INTO deals (
                deal_number, title, company_id, primary_contact_id, 
                value, currency, stage, probability,
                expected_close_date, deal_type, deal_source, 
                notes, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deal_number,
            data.get('title', data.get('name')),
            data.get('company_id'),
            data.get('primary_contact_id'),
            data.get('value', 0),
            data.get('currency', 'USD'),
            data.get('stage', 'Lead'),
            data.get('probability', data.get('win_probability', 10.0)),
            data.get('expected_close_date'),
            data.get('deal_type', 'new_business'),
            data.get('deal_source'),
            data.get('description', data.get('notes')),
            session.get('user_id')
        ))
        
        deal_id = cursor.lastrowid
        
        # Add primary contact to deal_contacts if specified
        if data.get('primary_contact_id'):
            cursor.execute('''
                INSERT INTO deal_contacts (deal_id, contact_id, role, is_primary)
                VALUES (?, ?, 'Primary Contact', 1)
            ''', (deal_id, data.get('primary_contact_id')))
        
        # Add additional contacts if provided
        if data.get('contact_ids'):
            for contact_id in data['contact_ids']:
                if contact_id != data.get('primary_contact_id'):
                    cursor.execute('''
                        INSERT INTO deal_contacts (deal_id, contact_id, role, is_primary)
                        VALUES (?, ?, 'Stakeholder', 0)
                    ''', (deal_id, contact_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deal created successfully',
            'deal_id': deal_id,
            'deal_number': deal_number
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals/<int:deal_id>', methods=['PUT'])
@login_required
def update_deal(deal_id):
    """Update a deal"""
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE deals SET
                title = ?, company_id = ?, primary_contact_id = ?,
                value = ?, currency = ?, stage = ?, probability = ?,
                expected_close_date = ?, actual_close_date = ?,
                deal_type = ?, deal_source = ?, notes = ?,
                lost_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('title', data.get('name')),
            data.get('company_id'),
            data.get('primary_contact_id'),
            data.get('value'),
            data.get('currency', 'USD'),
            data.get('stage'),
            data.get('probability', data.get('win_probability')),
            data.get('expected_close_date'),
            data.get('actual_close_date'),
            data.get('deal_type'),
            data.get('deal_source'),
            data.get('description', data.get('notes')),
            data.get('lost_reason'),
            deal_id
        ))
        
        # Update contacts if provided
        if 'contact_ids' in data:
            # Remove existing contacts
            cursor.execute('DELETE FROM deal_contacts WHERE deal_id = ?', (deal_id,))
            
            # Add primary contact
            if data.get('primary_contact_id'):
                cursor.execute('''
                    INSERT INTO deal_contacts (deal_id, contact_id, role, is_primary)
                    VALUES (?, ?, 'Primary Contact', 1)
                ''', (deal_id, data['primary_contact_id']))
            
            # Add other contacts
            for contact_id in data['contact_ids']:
                if contact_id != data.get('primary_contact_id'):
                    cursor.execute('''
                        INSERT INTO deal_contacts (deal_id, contact_id, role, is_primary)
                        VALUES (?, ?, 'Stakeholder', 0)
                    ''', (deal_id, contact_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deal updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals/<int:deal_id>/stage', methods=['PUT'])
@login_required
def update_deal_stage(deal_id):
    """Update deal stage (for drag & drop in pipeline)"""
    try:
        data = request.json
        new_stage = data.get('stage')
        
        if not new_stage:
            return jsonify({'success': False, 'message': 'Stage is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Get stage probability (case-insensitive lookup)
        cursor.execute('SELECT name, probability FROM deal_stages WHERE LOWER(name) = LOWER(?)', (new_stage,))
        stage_row = cursor.fetchone()
        
        if not stage_row:
            return jsonify({'success': False, 'message': 'Invalid stage'}), 400
        
        # Use the proper case name from the database
        proper_stage_name = stage_row[0]
        probability = stage_row[1]
        
        # Update deal
        update_data = {
            'stage': proper_stage_name,
            'probability': probability
        }
        
        # If moving to Closed Won, set actual close date
        if proper_stage_name == 'Closed Won':
            update_data['actual_close_date'] = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            UPDATE deals SET
                stage = ?,
                probability = ?,
                actual_close_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            update_data['stage'],
            update_data['probability'],
            update_data.get('actual_close_date'),
            deal_id
        ))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deal stage updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deals/<int:deal_id>', methods=['DELETE'])
@login_required
def delete_deal(deal_id):
    """Delete a deal"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Delete deal contacts first (cascade)
        cursor.execute('DELETE FROM deal_contacts WHERE deal_id = ?', (deal_id,))
        
        # Delete the deal
        cursor.execute('DELETE FROM deals WHERE id = ?', (deal_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Deal deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deals_bp.route('/api/deal-stages', methods=['GET'])
@login_required
def get_deal_stages():
    """Get all deal stages"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT id, name, order_index, probability, is_active
            FROM deal_stages
            WHERE is_active = 1
            ORDER BY order_index
        ''')
        
        stages = []
        for row in cursor.fetchall():
            stages.append({
                'id': row[0],
                'name': row[1],
                'order_index': row[2],
                'probability': row[3],
                'is_active': row[4]
            })
        
        return jsonify({'success': True, 'stages': stages})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
