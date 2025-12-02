"""
Enhanced Task Management Module
Handles task CRUD operations with assignments and priorities
"""

from flask import Blueprint, request, jsonify, session
from .db_helper import get_db
from functools import wraps
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@tasks_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks with filtering"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters
        status = request.args.get('status', '')
        assigned_to = request.args.get('assigned_to', type=int)
        customer_id = request.args.get('customer_id', type=int)
        opportunity_id = request.args.get('opportunity_id', type=int)
        priority = request.args.get('priority', '')
        
        query = '''
            SELECT t.id, t.title, t.description, t.assigned_to, t.due_date,
                   t.status, t.created_at, t.updated_at, t.priority, t.category,
                   t.customer_id, t.opportunity_id, t.completed_at, t.reminder_at, t.notes,
                   u.username as assigned_to_name,
                   c.name as customer_name,
                   o.title as opportunity_name
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            LEFT JOIN customers c ON t.customer_id = c.id
            LEFT JOIN opportunities o ON t.opportunity_id = o.id
            WHERE 1=1
        '''
        params = []
        
        if status:
            query += ' AND t.status = ?'
            params.append(status)
        
        if assigned_to:
            query += ' AND t.assigned_to = ?'
            params.append(assigned_to)
        
        if customer_id:
            query += ' AND t.customer_id = ?'
            params.append(customer_id)
        
        if opportunity_id:
            query += ' AND t.opportunity_id = ?'
            params.append(opportunity_id)
        
        if priority:
            query += ' AND t.priority = ?'
            params.append(priority)
        
        query += ' ORDER BY t.due_date ASC, t.priority DESC'
        
        cursor.execute(query, params)
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'assigned_to': row[3],
                'due_date': row[4],
                'status': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'priority': row[8],
                'category': row[9],
                'customer_id': row[10],
                'opportunity_id': row[11],
                'completed_at': row[12],
                'reminder_at': row[13],
                'notes': row[14],
                'assigned_to_name': row[15],
                'customer_name': row[16],
                'opportunity_name': row[17]
            })
        
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/my-tasks', methods=['GET'])
@login_required
def get_my_tasks():
    """Get tasks assigned to current user"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        user_id = session['user_id']
        status = request.args.get('status', '')
        
        query = '''
            SELECT t.id, t.title, t.description, t.assigned_to, t.due_date,
                   t.status, t.created_at, t.updated_at, t.priority, t.category,
                   t.customer_id, t.opportunity_id, t.completed_at, t.reminder_at, t.notes,
                   c.name as customer_name,
                   o.title as opportunity_name
            FROM tasks t
            LEFT JOIN customers c ON t.customer_id = c.id
            LEFT JOIN opportunities o ON t.opportunity_id = o.id
            WHERE t.assigned_to = ?
        '''
        params = [user_id]
        
        if status:
            query += ' AND t.status = ?'
            params.append(status)
        
        query += ' ORDER BY t.due_date ASC, t.priority DESC'
        
        cursor.execute(query, params)
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'assigned_to': row[3],
                'due_date': row[4],
                'status': row[5],
                'created_at': row[6],
                'updated_at': row[7],
                'priority': row[8],
                'category': row[9],
                'customer_id': row[10],
                'opportunity_id': row[11],
                'completed_at': row[12],
                'reminder_at': row[13],
                'notes': row[14],
                'customer_name': row[15],
                'opportunity_name': row[16]
            })
        
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get a specific task"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT t.id, t.title, t.description, t.assigned_to, t.due_date,
                   t.status, t.created_at, t.updated_at, t.priority, t.category,
                   t.customer_id, t.opportunity_id, t.completed_at, t.reminder_at, t.notes,
                   u.username as assigned_to_name,
                   c.name as customer_name,
                   o.title as opportunity_name
            FROM tasks t
            LEFT JOIN users u ON t.assigned_to = u.id
            LEFT JOIN customers c ON t.customer_id = c.id
            LEFT JOIN opportunities o ON t.opportunity_id = o.id
            WHERE t.id = ?
        ''', (task_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Task not found'}), 404
        
        task = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'assigned_to': row[3],
            'due_date': row[4],
            'status': row[5],
            'created_at': row[6],
            'updated_at': row[7],
            'priority': row[8],
            'category': row[9],
            'customer_id': row[10],
            'opportunity_id': row[11],
            'completed_at': row[12],
            'reminder_at': row[13],
            'notes': row[14],
            'assigned_to_name': row[15],
            'customer_name': row[16],
            'opportunity_name': row[17]
        }
        
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task"""
    db = None
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        if not data.get('due_date'):
            return jsonify({'success': False, 'message': 'Due date is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (
                title, description, assigned_to, due_date, status,
                priority, category, customer_id, opportunity_id,
                reminder_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('assigned_to', session['user_id']),
            data.get('due_date'),
            data.get('status', 'pending'),
            data.get('priority', 'medium'),
            data.get('category'),
            data.get('customer_id'),
            data.get('opportunity_id'),
            data.get('reminder_at'),
            data.get('notes')
        ))
        
        task_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task created successfully',
            'task_id': task_id
        }), 201
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a task"""
    db = None
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        # If marking as completed, set completed_at
        completed_at = None
        if data.get('status') == 'completed':
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            UPDATE tasks SET
                title = ?, description = ?, assigned_to = ?,
                due_date = ?, status = ?, priority = ?,
                category = ?, customer_id = ?, opportunity_id = ?,
                completed_at = ?, reminder_at = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('assigned_to'),
            data.get('due_date'),
            data.get('status'),
            data.get('priority'),
            data.get('category'),
            data.get('customer_id'),
            data.get('opportunity_id'),
            completed_at,
            data.get('reminder_at'),
            data.get('notes'),
            task_id
        ))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task updated successfully'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
@login_required
def update_task_status(task_id):
    """Update task status"""
    db = None
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        db = get_db()
        cursor = db.cursor()
        
        completed_at = None
        if status == 'completed':
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            UPDATE tasks SET
                status = ?,
                completed_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, completed_at, task_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task status updated successfully'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        })
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

@tasks_bp.route('/api/tasks/stats', methods=['GET'])
@login_required
def get_task_stats():
    """Get task statistics for current user"""
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        user_id = session['user_id']
        
        # Total tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ?', (user_id,))
        total = cursor.fetchone()[0]
        
        # Pending tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status = ?', (user_id, 'pending'))
        pending = cursor.fetchone()[0]
        
        # Completed tasks
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to = ? AND status = ?', (user_id, 'completed'))
        completed = cursor.fetchone()[0]
        
        # Overdue tasks
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE assigned_to = ? AND status != 'completed' 
            AND due_date < date('now')
        ''', (user_id,))
        overdue = cursor.fetchone()[0]
        
        # Due today
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE assigned_to = ? AND status != 'completed' 
            AND date(due_date) = date('now')
        ''', (user_id,))
        due_today = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'pending': pending,
                'completed': completed,
                'overdue': overdue,
                'due_today': due_today
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()
