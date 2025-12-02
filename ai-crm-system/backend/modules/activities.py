"""
Activities API Blueprint
Provides unified timeline tracking for companies, contacts, and deals
"""
from flask import Blueprint, request, jsonify, session
from .db_helper import get_db
from functools import wraps
from datetime import datetime

activities_bp = Blueprint('activities', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get current user info from session
        current_user = {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role', 'user')
        }
        return f(current_user, *args, **kwargs)
    return decorated_function

def get_db_helper():
    """Database helper with proper connection management"""
    conn = get_db()
    return conn

@activities_bp.route('/api/activities', methods=['GET'])
@login_required
def get_activities(current_user):
    """
    Get all activities with optional filters
    Query params: entity_type, entity_id, activity_type, limit, offset
    """
    conn = None
    try:
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Get query parameters
        entity_type = request.args.get('entity_type')  # company, contact, deal
        entity_id = request.args.get('entity_id', type=int)
        activity_type = request.args.get('activity_type')  # call, email, meeting, note, task
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = """
            SELECT 
                a.*,
                c.name as company_name,
                con.first_name || ' ' || con.last_name as contact_name,
                d.title as deal_title
            FROM activities a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN contacts con ON a.contact_id = con.id
            LEFT JOIN deals d ON a.deal_id = d.id
            WHERE 1=1
        """
        params = []
        
        if entity_type:
            query += " AND a.entity_type = ?"
            params.append(entity_type)
        
        if entity_id:
            query += " AND a.entity_id = ?"
            params.append(entity_id)
        
        if activity_type:
            query += " AND a.activity_type = ?"
            params.append(activity_type)
        
        query += " ORDER BY a.activity_date DESC, a.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        activities = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM activities WHERE 1=1"
        count_params = []
        if entity_type:
            count_query += " AND entity_type = ?"
            count_params.append(entity_type)
        if entity_id:
            count_query += " AND entity_id = ?"
            count_params.append(entity_id)
        if activity_type:
            count_query += " AND activity_type = ?"
            count_params.append(activity_type)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        return jsonify({
            'activities': [dict(row) for row in activities],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities/<int:activity_id>', methods=['GET'])
@login_required
def get_activity(current_user, activity_id):
    """Get a single activity by ID"""
    conn = None
    try:
        conn = get_db_helper()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.*,
                c.name as company_name,
                con.first_name || ' ' || con.last_name as contact_name,
                d.title as deal_title
            FROM activities a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN contacts con ON a.contact_id = con.id
            LEFT JOIN deals d ON a.deal_id = d.id
            WHERE a.id = ?
        """, (activity_id,))
        
        activity = cursor.fetchone()
        
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
        
        return jsonify(dict(activity)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities', methods=['POST'])
@login_required
def create_activity(current_user):
    """
    Create a new activity
    Required: activity_type, entity_type, entity_id, subject
    Optional: description, activity_date, duration_minutes, outcome, company_id, contact_id, deal_id
    """
    conn = None
    try:
        data = request.json
        
        # Validate required fields
        required = ['activity_type', 'entity_type', 'entity_id', 'subject']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate activity_type
        valid_types = ['call', 'email', 'meeting', 'note', 'task', 'demo', 'proposal']
        if data['activity_type'] not in valid_types:
            return jsonify({'error': f'Invalid activity_type. Must be one of: {", ".join(valid_types)}'}), 400
        
        # Validate entity_type
        valid_entities = ['company', 'contact', 'deal']
        if data['entity_type'] not in valid_entities:
            return jsonify({'error': f'Invalid entity_type. Must be one of: {", ".join(valid_entities)}'}), 400
        
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Set activity_date to now if not provided
        activity_date = data.get('activity_date', datetime.now().isoformat())
        
        cursor.execute("""
            INSERT INTO activities (
                activity_type, entity_type, entity_id, subject, description,
                activity_date, duration_minutes, outcome, 
                company_id, contact_id, deal_id, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['activity_type'],
            data['entity_type'],
            data['entity_id'],
            data['subject'],
            data.get('description'),
            activity_date,
            data.get('duration_minutes'),
            data.get('outcome'),
            data.get('company_id'),
            data.get('contact_id'),
            data.get('deal_id'),
            current_user['id']
        ))
        
        conn.commit()
        activity_id = cursor.lastrowid
        
        # Fetch the created activity
        cursor.execute("""
            SELECT 
                a.*,
                c.name as company_name,
                con.first_name || ' ' || con.last_name as contact_name,
                d.title as deal_title
            FROM activities a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN contacts con ON a.contact_id = con.id
            LEFT JOIN deals d ON a.deal_id = d.id
            WHERE a.id = ?
        """, (activity_id,))
        
        activity = cursor.fetchone()
        
        return jsonify({
            'message': 'Activity created successfully',
            'activity': dict(activity)
        }), 201
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities/<int:activity_id>', methods=['PUT'])
@login_required
def update_activity(current_user, activity_id):
    """Update an existing activity"""
    conn = None
    try:
        data = request.json
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Check if activity exists
        cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
        activity = cursor.fetchone()
        
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        allowed_fields = [
            'activity_type', 'subject', 'description', 'activity_date',
            'duration_minutes', 'outcome', 'company_id', 'contact_id', 'deal_id'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(activity_id)
        
        query = f"UPDATE activities SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        
        # Fetch updated activity
        cursor.execute("""
            SELECT 
                a.*,
                c.name as company_name,
                con.first_name || ' ' || con.last_name as contact_name,
                d.title as deal_title
            FROM activities a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN contacts con ON a.contact_id = con.id
            LEFT JOIN deals d ON a.deal_id = d.id
            WHERE a.id = ?
        """, (activity_id,))
        
        activity = cursor.fetchone()
        
        return jsonify({
            'message': 'Activity updated successfully',
            'activity': dict(activity)
        }), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities/<int:activity_id>', methods=['DELETE'])
@login_required
def delete_activity(current_user, activity_id):
    """Delete an activity"""
    conn = None
    try:
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Check if activity exists
        cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
        activity = cursor.fetchone()
        
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
        
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        
        return jsonify({'message': 'Activity deleted successfully'}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities/timeline', methods=['GET'])
@login_required
def get_timeline(current_user):
    """
    Get unified timeline across all entities
    Query params: company_id, contact_id, deal_id, start_date, end_date, limit
    """
    conn = None
    try:
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Get query parameters
        company_id = request.args.get('company_id', type=int)
        contact_id = request.args.get('contact_id', type=int)
        deal_id = request.args.get('deal_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        query = """
            SELECT 
                a.*,
                c.name as company_name,
                con.first_name || ' ' || con.last_name as contact_name,
                d.title as deal_title
            FROM activities a
            LEFT JOIN companies c ON a.company_id = c.id
            LEFT JOIN contacts con ON a.contact_id = con.id
            LEFT JOIN deals d ON a.deal_id = d.id
            WHERE 1=1
        """
        params = []
        
        if company_id:
            query += " AND (a.company_id = ? OR a.entity_type = 'company' AND a.entity_id = ?)"
            params.extend([company_id, company_id])
        
        if contact_id:
            query += " AND (a.contact_id = ? OR a.entity_type = 'contact' AND a.entity_id = ?)"
            params.extend([contact_id, contact_id])
        
        if deal_id:
            query += " AND (a.deal_id = ? OR a.entity_type = 'deal' AND a.entity_id = ?)"
            params.extend([deal_id, deal_id])
        
        if start_date:
            query += " AND a.activity_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND a.activity_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY a.activity_date DESC, a.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        timeline = cursor.fetchall()
        
        return jsonify({
            'timeline': [dict(row) for row in timeline],
            'count': len(timeline)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@activities_bp.route('/api/activities/stats', methods=['GET'])
@login_required
def get_activity_stats(current_user):
    """Get activity statistics by type and date range"""
    conn = None
    try:
        conn = get_db_helper()
        cursor = conn.cursor()
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT 
                activity_type,
                COUNT(*) as count,
                AVG(duration_minutes) as avg_duration
            FROM activities
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND activity_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND activity_date <= ?"
            params.append(end_date)
        
        query += " GROUP BY activity_type ORDER BY count DESC"
        
        cursor.execute(query, params)
        stats = cursor.fetchall()
        
        # Get total activities
        cursor.execute("SELECT COUNT(*) as total FROM activities")
        total = cursor.fetchone()['total']
        
        return jsonify({
            'stats': [dict(row) for row in stats],
            'total_activities': total
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()
