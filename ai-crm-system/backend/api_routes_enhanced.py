# api_routes_enhanced.py
"""
Enhanced API Routes for CRM Features
Add these routes to app.py
"""

from flask import request, jsonify, session
from datetime import datetime
import os
from werkzeug.utils import secure_filename

# These functions should be added to app.py

def setup_enhanced_routes(app, db_enhanced, db, auth):
    """Setup enhanced CRM routes"""
    
    # ==================== COMPANIES API ====================
    
    @app.route('/api/companies', methods=['GET', 'POST', 'OPTIONS'])
    def manage_companies():
        """Companies management endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            companies = db_enhanced.get_all_companies()
            return jsonify(companies)
        
        elif request.method == 'POST':
            data = request.get_json()
            company_id = db_enhanced.add_company(data)
            
            # Log activity
            if 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'], 
                    'create', 
                    'company', 
                    company_id,
                    f"Created company: {data.get('name')}"
                )
            
            return jsonify({'success': True, 'company_id': company_id})
    
    @app.route('/api/companies/<int:company_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def company_detail(company_id):
        """Company detail endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            company = db_enhanced.get_company(company_id)
            if company:
                # Get related contacts
                conn = db_enhanced.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, name, email, phone, job_title 
                    FROM customers 
                    WHERE company_id = ?
                ''', (company_id,))
                contacts = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                company['contacts'] = contacts
                return jsonify(company)
            return jsonify({'error': 'Company not found'}), 404
        
        elif request.method == 'PUT':
            data = request.get_json()
            success = db_enhanced.update_company(company_id, data)
            
            if success and 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'],
                    'update',
                    'company',
                    company_id,
                    f"Updated company"
                )
            
            return jsonify({'success': success})
        
        elif request.method == 'DELETE':
            success = db_enhanced.delete_company(company_id)
            
            if success and 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'],
                    'delete',
                    'company',
                    company_id,
                    f"Deleted company"
                )
            
            return jsonify({'success': success})
    
    # ==================== DEALS API ====================
    
    @app.route('/api/deals', methods=['GET', 'POST', 'OPTIONS'])
    def manage_deals():
        """Deals management endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            status = request.args.get('status', 'open')
            deals = db_enhanced.get_all_deals(status)
            return jsonify(deals)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Set owner to current user if not specified
            if 'owner_id' not in data and 'user_id' in session:
                data['owner_id'] = session['user_id']
            
            deal_id = db_enhanced.add_deal(data)
            
            # Log activity
            if 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'],
                    'create',
                    'deal',
                    deal_id,
                    f"Created deal: {data.get('title')}"
                )
            
            return jsonify({'success': True, 'deal_id': deal_id})
    
    @app.route('/api/deals/<int:deal_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
    def deal_detail(deal_id):
        """Deal detail endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            deal = db_enhanced.get_deal(deal_id)
            if deal:
                # Get notes and attachments
                deal['notes'] = db_enhanced.get_notes('deal', deal_id)
                deal['attachments'] = db_enhanced.get_attachments('deal', deal_id)
                deal['activities'] = db_enhanced.get_activity_log('deal', deal_id, 20)
                return jsonify(deal)
            return jsonify({'error': 'Deal not found'}), 404
        
        elif request.method == 'PUT':
            data = request.get_json()
            user_id = session.get('user_id', 0)
            success = db_enhanced.update_deal(deal_id, data, user_id)
            
            if success:
                db_enhanced.log_activity(
                    user_id,
                    'update',
                    'deal',
                    deal_id,
                    f"Updated deal"
                )
            
            return jsonify({'success': success})
        
        elif request.method == 'DELETE':
            # Soft delete by marking as closed_lost
            success = db_enhanced.update_deal(
                deal_id, 
                {'status': 'closed_lost'}, 
                session.get('user_id', 0)
            )
            return jsonify({'success': success})
    
    @app.route('/api/pipeline', methods=['GET', 'OPTIONS'])
    def get_pipeline():
        """Get pipeline view grouped by stage"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        pipeline = db_enhanced.get_deals_by_stage()
        
        # Calculate totals for each stage
        pipeline_summary = {}
        for stage, deals in pipeline.items():
            total_value = sum([deal.get('value', 0) for deal in deals])
            pipeline_summary[stage] = {
                'deals': deals,
                'count': len(deals),
                'total_value': total_value
            }
        
        return jsonify(pipeline_summary)
    
    # ==================== TASKS API ====================
    
    @app.route('/api/tasks', methods=['GET', 'POST', 'OPTIONS'])
    def manage_tasks():
        """Tasks management endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            status = request.args.get('status')
            
            if user_id:
                tasks = db_enhanced.get_tasks_by_user(int(user_id), status or 'pending')
            else:
                tasks = db_enhanced.get_all_tasks(status)
            
            return jsonify(tasks)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Set assigned_by to current user
            if 'user_id' in session:
                data['assigned_by'] = session['user_id']
            
            task_id = db.add_task(data)
            
            # Log activity
            if 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'],
                    'create',
                    'task',
                    task_id,
                    f"Created task: {data.get('title')}"
                )
            
            return jsonify({'success': True, 'task_id': task_id})
    
    @app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
    def task_detail(task_id):
        """Task detail endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'PUT':
            data = request.get_json()
            
            # Update task
            conn = db.get_connection()
            cursor = conn.cursor()
            
            fields = []
            values = []
            
            for key, value in data.items():
                if key not in ['id', 'created_at']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if fields:
                values.append(task_id)
                query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            
            # Log activity
            if 'user_id' in session:
                db_enhanced.log_activity(
                    session['user_id'],
                    'update',
                    'task',
                    task_id,
                    f"Updated task"
                )
            
            return jsonify({'success': True})
        
        elif request.method == 'DELETE':
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True})
    
    # ==================== NOTES API ====================
    
    @app.route('/api/notes', methods=['GET', 'POST', 'OPTIONS'])
    def manage_notes():
        """Notes management endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            entity_type = request.args.get('entity_type')
            entity_id = request.args.get('entity_id')
            
            if entity_type and entity_id:
                notes = db_enhanced.get_notes(entity_type, int(entity_id))
                return jsonify(notes)
            return jsonify({'error': 'Missing parameters'}), 400
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Set created_by to current user
            if 'user_id' in session:
                data['created_by'] = session['user_id']
            
            note_id = db_enhanced.add_note(data)
            
            return jsonify({'success': True, 'note_id': note_id})
    
    # ==================== ATTACHMENTS API ====================
    
    @app.route('/api/attachments', methods=['GET', 'POST', 'OPTIONS'])
    def manage_attachments():
        """Attachments management endpoint"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        if request.method == 'GET':
            entity_type = request.args.get('entity_type')
            entity_id = request.args.get('entity_id')
            
            if entity_type and entity_id:
                attachments = db_enhanced.get_attachments(entity_type, int(entity_id))
                return jsonify(attachments)
            return jsonify({'error': 'Missing parameters'}), 400
        
        elif request.method == 'POST':
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            entity_type = request.form.get('entity_type')
            entity_id = request.form.get('entity_id')
            description = request.form.get('description', '')
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Save to database
            attachment_data = {
                'filename': unique_filename,
                'original_filename': filename,
                'file_path': file_path,
                'file_size': file_size,
                'mime_type': file.content_type,
                'entity_type': entity_type,
                'entity_id': int(entity_id),
                'uploaded_by': session.get('user_id'),
                'description': description
            }
            
            attachment_id = db_enhanced.add_attachment(attachment_data)
            
            return jsonify({'success': True, 'attachment_id': attachment_id})
    
    # ==================== ACTIVITY LOG API ====================
    
    @app.route('/api/activity-log', methods=['GET', 'OPTIONS'])
    def get_activity():
        """Get activity log"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id')
        limit = int(request.args.get('limit', 50))
        
        if entity_type and entity_id:
            activities = db_enhanced.get_activity_log(entity_type, int(entity_id), limit)
        else:
            activities = db_enhanced.get_activity_log(limit=limit)
        
        return jsonify(activities)
    
    # ==================== USER MANAGEMENT API ====================
    
    @app.route('/api/users', methods=['GET', 'OPTIONS'])
    def get_users():
        """Get all users (for assignments, etc.)"""
        if request.method == 'OPTIONS':
            return jsonify({'status': 'ok'}), 200
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, email, role, created_at
            FROM users
            ORDER BY username
        ''')
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(users)
    
    return app
