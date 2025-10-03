# app.py
"""
AI-Based CRM System - Main Application (API Backend)
This is the main entry point for the CRM API backend
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Import custom modules
from modules.database import Database
from modules.ai_services import AIServices
from modules.lead_scoring import LeadScoring
from modules.sales_forecasting import SalesForecasting
from modules.chatbot import ChatBot
from modules.workflow_automation import WorkflowAutomation
from modules.auth import Auth

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configure CORS to allow requests from React frontend
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:5173'],  # React dev server ports
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize services
db = Database()
ai_services = AIServices()
lead_scorer = LeadScoring()
sales_forecaster = SalesForecasting()
chatbot = ChatBot()
workflow = WorkflowAutomation(db)
auth = Auth()

# Initialize database tables
db.init_tables()

# Create default admin user (will only create if doesn't exist)
try:
    auth.create_user('admin', 'admin123', 'admin@crm.com', 'admin')
except:
    pass  # User already exists

# Routes
@app.route('/')
def index():
    """API root endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'AI CRM API Backend',
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """User login"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = auth.authenticate(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['user_role'] = user['role']
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=8)
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# Rest of the routes remain the same but remove any render_template calls
# All routes should return JSON responses only

@app.route('/api/customers', methods=['GET', 'POST', 'OPTIONS'])
def manage_customers():
    """Customer management endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    # Remove session check temporarily for testing, or implement JWT tokens
    # if 'user_id' not in session:
    #     return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        customers = db.get_all_customers()
        return jsonify(customers)
    
    elif request.method == 'POST':
        data = request.get_json()
        customer_id = db.add_customer(data)
        
        # Score the lead immediately
        lead_score = lead_scorer.calculate_score(data)
        db.update_customer_score(customer_id, lead_score)
        
        # Schedule follow-up if needed
        if lead_score > 70:
            workflow.schedule_follow_up(customer_id, priority='high')
        
        # Create new lead workflow
        workflow.create_workflow('new_lead', customer_id)
        
        return jsonify({'success': True, 'customer_id': customer_id, 'lead_score': lead_score})

# ... rest of the API endpoints remain the same ...

if __name__ == '__main__':
    # Start workflow scheduler
    workflow.start_scheduler()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)