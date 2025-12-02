# app.py
"""
AI-Based CRM System - Main Application (API Backend)
This is the main entry point for the CRM API backend
"""

from flask import Flask, request, jsonify, session, g
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in the project root (2 levels up from backend/)
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

# Import custom modules
from modules.database import Database
from modules.database_enhanced import EnhancedDatabase
from modules.groq_ai import GroqAI
from modules.ai_services import AIServices
from modules.lead_scoring import LeadScoring
from modules.sales_forecasting import SalesForecasting
from modules.chatbot import ChatBot
from modules.workflow_automation import WorkflowAutomation
from modules.auth import Auth

# Import new AI-powered modules
from modules.ai_chatbot_enhanced import EnhancedChatbot
from modules.predictive_insights import PredictiveInsights
from modules.smart_automation import SmartAutomation

# Import new enhanced CRM modules
from modules.companies import companies_bp
from modules.deals import deals_bp
from modules.tasks_enhanced import tasks_bp as tasks_enhanced_bp
from modules.contacts import contacts_bp
from modules.activities import activities_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Configure CORS to allow requests from React frontend
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:5173', 'http://localhost:3001'],  # React dev server ports
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize services
db = Database()
db_enhanced = EnhancedDatabase()
# Load the AI model once and share it across modules
ai_model = GroqAI()
ai_services = AIServices(ai_model)
lead_scorer = LeadScoring(ai_model)
sales_forecaster = SalesForecasting()
chatbot = ChatBot(ai_model)
workflow = WorkflowAutomation(db)
auth = Auth()

# Initialize new AI-powered services
enhanced_chatbot = EnhancedChatbot(ai_model)
predictive_insights = PredictiveInsights(ai_model)
smart_automation = SmartAutomation(ai_model)

# Initialize database tables
db.init_tables()
db_enhanced.create_enhanced_tables()

# Register blueprints for enhanced CRM features
app.register_blueprint(companies_bp)
app.register_blueprint(deals_bp)
app.register_blueprint(tasks_enhanced_bp)
app.register_blueprint(contacts_bp)
app.register_blueprint(activities_bp)

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

@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    """User registration"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'sales_rep')  # Default role
    
    # Validation
    if not username or not password or not email:
        return jsonify({
            'success': False, 
            'message': 'Username, password, and email are required'
        }), 400
    
    # Username validation
    if len(username) < 3 or len(username) > 30:
        return jsonify({
            'success': False,
            'message': 'Username must be between 3 and 30 characters'
        }), 400
    
    # Password validation
    if len(password) < 6:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 6 characters'
        }), 400
    
    # Email validation (basic)
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({
            'success': False,
            'message': 'Invalid email format'
        }), 400
    
    # Allowed roles
    allowed_roles = ['admin', 'sales_rep', 'manager']
    if role not in allowed_roles:
        role = 'sales_rep'
    
    # Create user
    success = auth.create_user(username, password, email, role)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login.',
            'user': {
                'username': username,
                'email': email,
                'role': role
            }
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': 'Username or email already exists'
        }), 409

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
        
        # Convert budget to float if it exists
        if 'budget' in data and data['budget']:
            try:
                data['budget'] = float(data['budget'])
            except (ValueError, TypeError):
                data['budget'] = 0
        
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

@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def customer_detail(customer_id):
    """Customer detail endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    if request.method == 'GET':
        customer = db.get_customer(customer_id)
        if customer:
            return jsonify(customer)
        return jsonify({'error': 'Customer not found'}), 404
    
    elif request.method == 'PUT':
        data = request.get_json()
        success = db.update_customer(customer_id, data)
        if success:
            # Recalculate lead score
            customer = db.get_customer(customer_id)
            lead_score = lead_scorer.calculate_score(customer)
            db.update_customer_score(customer_id, lead_score)
            return jsonify({'success': True, 'lead_score': lead_score})
        return jsonify({'error': 'Update failed'}), 400
    
    elif request.method == 'DELETE':
        success = db.delete_customer(customer_id)
        if success:
            return jsonify({'success': True})
        return jsonify({'error': 'Delete failed'}), 400

@app.route('/api/interactions', methods=['GET', 'POST', 'OPTIONS'])
def manage_interactions():
    """Interactions management endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    if request.method == 'GET':
        customer_id = request.args.get('customer_id')
        if customer_id:
            interactions = db.get_customer_interactions(int(customer_id))
        else:
            interactions = db.get_all_interactions()
        return jsonify(interactions)
    
    elif request.method == 'POST':
        data = request.get_json()
        interaction_id = db.add_interaction(data)
        
        # Update customer engagement
        if data.get('customer_id'):
            customer = db.get_customer(data['customer_id'])
            interactions = db.get_customer_interactions(data['customer_id'])
            lead_score = lead_scorer.calculate_score(customer, interactions)
            db.update_customer_score(data['customer_id'], lead_score)
        
        return jsonify({'success': True, 'interaction_id': interaction_id})

@app.route('/api/dashboard/analytics', methods=['GET', 'OPTIONS'])
def dashboard_analytics():
    """Dashboard analytics endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.db_helper import get_db
        conn = get_db()
        cursor = conn.cursor()
        
        # Get customers/contacts data
        customers = db.get_all_customers()
        interactions = db.get_recent_interactions(10)
        
        # Calculate customer metrics
        total_customers = len(customers)
        active_leads = len([c for c in customers if c.get('status') in ['lead', 'qualified', 'interested']])
        converted_customers = len([c for c in customers if c.get('status') == 'customer'])
        
        # Get deal-based metrics from the deals table
        cursor.execute('''
            SELECT 
                COUNT(*) as total_deals,
                SUM(CASE WHEN stage = 'Closed Won' THEN 1 ELSE 0 END) as won_deals,
                SUM(CASE WHEN stage = 'Closed Won' THEN value ELSE 0 END) as total_revenue,
                SUM(CASE WHEN stage NOT IN ('Closed Won', 'Closed Lost') THEN value ELSE 0 END) as pipeline_value
            FROM deals
        ''')
        
        deal_stats = cursor.fetchone()
        total_deals = deal_stats[0] or 0
        won_deals = deal_stats[1] or 0
        total_revenue = deal_stats[2] or 0
        pipeline_value = deal_stats[3] or 0
        
        # Calculate conversion rate from deals
        conversion_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
        
        # Get top leads from contacts with lead scores
        cursor.execute('''
            SELECT id, first_name || ' ' || last_name as name, email, company_id, lead_score
            FROM contacts
            WHERE lead_score > 0
            ORDER BY lead_score DESC
            LIMIT 5
        ''')
        top_leads = [dict(row) for row in cursor.fetchall()]
        
        # Sales forecast
        forecast_data = sales_forecaster.get_quick_forecast()
        
        analytics = {
            'total_customers': total_customers,
            'active_leads': active_leads,
            'conversion_rate': round(conversion_rate, 1),
            'monthly_revenue': total_revenue,  # Now from actual closed deals
            'pipeline_value': pipeline_value,  # Active deals value
            'top_leads': top_leads,
            'recent_interactions': interactions,
            'sales_forecast': forecast_data
        }
        
        return jsonify(analytics)
    except Exception as e:
        print(f"Dashboard analytics error: {e}")
        # Fallback to basic metrics
        customers = db.get_all_customers()
        interactions = db.get_recent_interactions(10)
        
        total_customers = len(customers)
        active_leads = len([c for c in customers if c.get('status') in ['lead', 'qualified', 'interested']])
        top_leads = sorted(customers, key=lambda x: x.get('lead_score', 0), reverse=True)[:5]
        
        return jsonify({
            'total_customers': total_customers,
            'active_leads': active_leads,
            'conversion_rate': 0,
            'monthly_revenue': 0,
            'pipeline_value': 0,
            'top_leads': top_leads,
            'recent_interactions': interactions,
            'sales_forecast': []
        })

@app.route('/api/notifications', methods=['GET', 'OPTIONS'])
def get_notifications():
    """Get user notifications"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    # Get limit parameter (default to 10, None means all)
    limit_param = request.args.get('limit', '10')
    limit = None if limit_param == 'all' else int(limit_param)
    
    # Determine how many of each type of notification to generate
    # When showing all, generate more notifications; otherwise keep it limited
    customer_limit = None if limit is None else 5
    lead_limit = None if limit is None else 3
    interaction_limit = None if limit is None else 5
    
    # Get recent activities and create notifications
    customers = db.get_all_customers()
    interactions = db.get_recent_interactions(20)
    
    notifications = []
    
    # New customer notifications
    customer_slice = customers if customer_limit is None else customers[:customer_limit]
    for customer in customer_slice:
        notifications.append({
            'id': f"new_customer_{customer.get('id')}",
            'type': 'new_customer',
            'title': 'New Customer Added',
            'message': f"{customer.get('name')} from {customer.get('company', 'Unknown Company')} was added",
            'time': 'Recently',
            'read': False,
            'icon': 'user',
            'color': 'bg-blue-500'
        })
    
    # High-score lead notifications
    high_score_leads = [c for c in customers if c.get('lead_score', 0) > 70]
    lead_slice = high_score_leads if lead_limit is None else high_score_leads[:lead_limit]
    for lead in lead_slice:
        notifications.append({
            'id': f"hot_lead_{lead.get('id')}",
            'type': 'hot_lead',
            'title': 'Hot Lead Detected',
            'message': f"{lead.get('name')} has a lead score of {lead.get('lead_score', 0)}",
            'time': '2 hours ago',
            'read': False,
            'icon': 'fire',
            'color': 'bg-red-500'
        })
    
    # Recent interaction notifications
    interaction_slice = interactions if interaction_limit is None else interactions[:interaction_limit]
    for interaction in interaction_slice:
        customer = db.get_customer(interaction.get('customer_id'))
        if customer:
            notifications.append({
                'id': f"interaction_{interaction.get('id')}",
                'type': 'interaction',
                'title': 'New Interaction',
                'message': f"New {interaction.get('type', 'activity')} with {customer.get('name')}",
                'time': '1 day ago',
                'read': True,
                'icon': 'message',
                'color': 'bg-green-500'
            })
    
    # Apply final limit if specified
    if limit is not None:
        notifications = notifications[:limit]
    
    return jsonify({'notifications': notifications})

@app.route('/api/generate-ai-report', methods=['POST', 'OPTIONS'])
def generate_ai_report():
    """Generate AI-powered business report"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    # Get business data
    customers = db.get_all_customers()
    interactions = db.get_recent_interactions(50)
    
    # Calculate metrics
    total_customers = len(customers)
    active_leads = len([c for c in customers if c.get('status') in ['lead', 'qualified', 'interested']])
    converted_customers = len([c for c in customers if c.get('status') == 'customer'])
    conversion_rate = (converted_customers / total_customers * 100) if total_customers > 0 else 0
    monthly_revenue = sum([c.get('budget', 0) for c in customers if c.get('status') == 'customer'])
    
    # Get sales forecast
    forecast_data = sales_forecaster.get_quick_forecast()
    
    # Generate AI insights using AI services
    business_data = {
        'customers': customers,
        'interactions': interactions,
        'revenue': monthly_revenue
    }
    
    ai_insights = ai_services.generate_business_insights(business_data)
    
    # Create comprehensive report
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_customers': total_customers,
            'active_leads': active_leads,
            'conversion_rate': round(conversion_rate, 1),
            'monthly_revenue': monthly_revenue,
            'top_performing_industry': 'Technology',  # Calculate from customers
            'average_lead_score': round(sum([c.get('lead_score', 0) for c in customers]) / max(total_customers, 1), 1)
        },
        'insights': ai_insights,
        'forecast': forecast_data,
        'recommendations': [
            'Focus on high-score leads (>70) for immediate conversion',
            'Increase engagement with leads in Technology and Finance sectors',
            'Schedule follow-ups for leads inactive for >7 days',
            'Expand outreach in your top-performing industries',
            'Implement automated nurturing campaigns for cold leads'
        ],
        'trends': {
            'customer_growth': '+12% this month',
            'lead_quality': 'Improving - average score increased by 8 points',
            'engagement': 'High - 85% of leads have recent interactions',
            'pipeline_health': 'Strong - forecast shows moderate growth'
        }
    }
    
    return jsonify(report)

@app.route('/api/chatbot/message', methods=['POST', 'OPTIONS'])
def chatbot_message():
    """Chatbot message endpoint with conversation state management"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    message = data.get('message', '')
    customer_id = data.get('customer_id')
    
    # Check if we're in the middle of a multi-step conversation
    conversation_context = None
    if 'chatbot_state' in session:
        conversation_context = {'in_conversation': True}
        state = session['chatbot_state']
        
        # Handle email body input
        if state.get('next_step') == 'waiting_for_email_body' and state.get('pending_email'):
            pending = state['pending_email']
            
            # Send the email with the user's message as body
            email_log = {
                'recipient': pending['recipient'],
                'subject': pending['subject'],
                'body': message,
                'sent_at': datetime.now().isoformat()
            }
            
            response = {
                'message': f"✓ Email sent to {pending['customer_name']} ({pending['recipient']})!\n\nSubject: {pending['subject']}\nBody: {message}",
                'intent': 'send_email',
                'action': 'send_email_completed',
                'action_executed': True,
                'email_data': email_log,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log interaction
            if pending.get('customer_id'):
                db.add_interaction({
                    'customer_id': pending['customer_id'],
                    'type': 'email',
                    'channel': 'email',
                    'notes': f"Sent email: {pending['subject']}\nBody: {message}"
                })
            
            # Clear the state
            session.pop('chatbot_state', None)
            return jsonify(response)
        
        # Handle customer name input for email
        elif state.get('next_step') == 'waiting_for_customer_name':
            # User provided a customer name
            customers = db.get_all_customers()
            matching_customers = [c for c in customers if message.lower() in c.get('name', '').lower()]
            
            if matching_customers:
                customer = matching_customers[0]
                customer_email = customer.get('email')
                
                if customer_email:
                    response = {
                        'message': f"Found {customer['name']} ({customer_email}). What would you like to say in the email?",
                        'intent': 'send_email',
                        'action': 'send_email_waiting_body',
                        'action_executed': False,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Update state
                    session['chatbot_state'] = {
                        'next_step': 'waiting_for_email_body',
                        'pending_email': {
                            'customer_id': customer['id'],
                            'customer_name': customer['name'],
                            'recipient': customer_email,
                            'subject': 'CRM Email'
                        }
                    }
                    return jsonify(response)
                else:
                    response = {
                        'message': f"Found {customer['name']}, but they don't have an email address on file. Please add their email first.",
                        'intent': 'send_email',
                        'action': 'send_email_error',
                        'action_executed': False,
                        'timestamp': datetime.now().isoformat()
                    }
                    session.pop('chatbot_state', None)
                    return jsonify(response)
            else:
                response = {
                    'message': f"I couldn't find a customer named '{message}'. Please check the name and try again.",
                    'intent': 'send_email',
                    'action': 'send_email_error',
                    'action_executed': False,
                    'timestamp': datetime.now().isoformat()
                }
                session.pop('chatbot_state', None)
                return jsonify(response)
        
        # Handle customer name input for delete
        elif state.get('next_step') == 'waiting_for_delete_customer_name':
            # User provided a customer name to delete
            customers = db.get_all_customers()
            matching_customers = [c for c in customers if message.lower() in c.get('name', '').lower()]
            
            if matching_customers:
                customer = matching_customers[0]
                
                response = {
                    'message': f"Are you sure you want to delete {customer['name']} (ID: {customer['id']})? Type 'yes' to confirm or 'no' to cancel.",
                    'intent': 'delete_customer',
                    'action': 'delete_customer_confirm',
                    'action_executed': False,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update state to wait for confirmation
                session['chatbot_state'] = {
                    'next_step': 'waiting_for_delete_confirmation',
                    'pending_delete': {
                        'customer_id': customer['id'],
                        'customer_name': customer['name']
                    }
                }
                return jsonify(response)
            else:
                response = {
                    'message': f"I couldn't find a customer named '{message}'. Please check the name and try again.",
                    'intent': 'delete_customer',
                    'action': 'delete_customer_error',
                    'action_executed': False,
                    'timestamp': datetime.now().isoformat()
                }
                session.pop('chatbot_state', None)
                return jsonify(response)
        
        # Handle delete confirmation
        elif state.get('next_step') == 'waiting_for_delete_confirmation' and state.get('pending_delete'):
            pending = state['pending_delete']
            
            if message.lower() in ['yes', 'y', 'confirm', 'sure']:
                try:
                    # Delete the customer
                    db.delete_customer(pending['customer_id'])
                    
                    response = {
                        'message': f"✓ Customer '{pending['customer_name']}' has been successfully deleted.",
                        'intent': 'delete_customer',
                        'action': 'delete_customer_completed',
                        'action_executed': True,
                        'deleted_customer': pending,
                        'timestamp': datetime.now().isoformat()
                    }
                except Exception as e:
                    response = {
                        'message': f"❌ Error deleting customer: {str(e)}",
                        'intent': 'delete_customer',
                        'action': 'delete_customer_error',
                        'action_executed': False,
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                response = {
                    'message': f"Delete cancelled. {pending['customer_name']} was not deleted.",
                    'intent': 'delete_customer',
                    'action': 'delete_customer_cancelled',
                    'action_executed': False,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Clear the state
            session.pop('chatbot_state', None)
            return jsonify(response)
        
        # Handle entity creation follow-up (when user provides entity type or name)
        elif state.get('next_step') == 'waiting_for_entity_info':
            # User is providing follow-up info for entity creation
            entity_type = state.get('entity_type')
            collected_data = state.get('collected_data', {})
            needs_input = state.get('needs_input')
            
            # Re-route through enhanced chatbot with context
            if entity_type:
                # Map needs_input to data key and store the user's current response
                if needs_input:
                    # Extract the field name from needs_input (e.g., 'company_name' -> 'name')
                    field_mappings = {
                        'company_name': 'name',
                        'company_industry': 'industry',
                        'company_website': 'website',
                        'company_email': 'email',
                        'company_phone': 'phone',
                        'contact_first_name': 'first_name',
                        'contact_last_name': 'last_name',
                        'contact_email': 'email',
                        'contact_phone': 'phone',
                        'contact_job_title': 'job_title',
                        'contact_company': 'company',
                        'task_title': 'title',
                        'task_description': 'description',
                        'task_priority': 'priority',
                        'task_due_date': 'due_date',
                    }
                    
                    field_key = field_mappings.get(needs_input)
                    if field_key:
                        collected_data[field_key] = message
                
                # Build a comprehensive message that includes all collected data
                parts = [f"Create {entity_type}"]
                if collected_data.get('name'):
                    parts.append(f"name: {collected_data['name']}")
                if collected_data.get('first_name'):
                    parts.append(f"first name: {collected_data['first_name']}")
                if collected_data.get('last_name'):
                    parts.append(f"last name: {collected_data['last_name']}")
                if collected_data.get('industry'):
                    parts.append(f"industry: {collected_data['industry']}")
                if collected_data.get('website'):
                    parts.append(f"website: {collected_data['website']}")
                if collected_data.get('email'):
                    parts.append(f"email: {collected_data['email']}")
                if collected_data.get('phone'):
                    parts.append(f"phone: {collected_data['phone']}")
                if collected_data.get('job_title'):
                    parts.append(f"title: {collected_data['job_title']}")
                if collected_data.get('company'):
                    parts.append(f"company: {collected_data['company']}")
                if collected_data.get('title'):
                    parts.append(f"title: {collected_data['title']}")
                if collected_data.get('description'):
                    parts.append(f"description: {collected_data['description']}")
                if collected_data.get('priority'):
                    parts.append(f"priority: {collected_data['priority']}")
                if collected_data.get('due_date'):
                    parts.append(f"due date: {collected_data['due_date']}")
                
                full_message = " ".join(parts)
                response = enhanced_chatbot.process_query(full_message)
                
                # Clear state if creation successful
                if '✅' in response.get('message', ''):
                    session.pop('chatbot_state', None)
                else:
                    # Keep state and accumulate data if still needs more info
                    if response.get('needs_input'):
                        # Merge any additional data returned by the chatbot
                        if response.get('data'):
                            for key, value in response['data'].items():
                                if value and key not in collected_data:
                                    collected_data[key] = value
                        
                        session['chatbot_state'] = {
                            'next_step': 'waiting_for_entity_info',
                            'entity_type': entity_type,
                            'needs_input': response.get('needs_input'),
                            'collected_data': collected_data
                        }
                
                return jsonify(response)
            else:
                # User just said entity type like "Company", "Contact", etc.
                message_lower = message.lower()
                if any(etype in message_lower for etype in ['company', 'companies']):
                    entity_type = 'company'
                elif any(etype in message_lower for etype in ['contact', 'person']):
                    entity_type = 'contact'
                elif any(etype in message_lower for etype in ['deal', 'opportunity']):
                    entity_type = 'deal'
                elif any(etype in message_lower for etype in ['task']):
                    entity_type = 'task'
                else:
                    # Unknown entity type
                    response = {
                        'message': "What would you like to create?\n• Company\n• Contact\n• Deal/Opportunity\n• Task\n• Log interaction",
                        'intent': 'create_record',
                        'timestamp': datetime.now().isoformat()
                    }
                    return jsonify(response)
                
                # Ask for the name
                prompts = {
                    'company': "What's the company name?",
                    'contact': "What's the contact's name?",
                    'deal': "What's the deal title?",
                    'task': "What task would you like to create?"
                }
                
                response = {
                    'message': prompts.get(entity_type, "Please provide more details."),
                    'intent': 'create_record',
                    'needs_input': f'{entity_type}_name',
                    'timestamp': datetime.now().isoformat()
                }
                
                # Update state to wait for name
                session['chatbot_state'] = {
                    'next_step': 'waiting_for_entity_info',
                    'entity_type': entity_type,
                    'needs_input': f'{entity_type}_name'
                }
                
                return jsonify(response)
    
    # Check if this is a CRM query/navigation request - use enhanced chatbot
    message_lower = message.lower()
    
    # Check for email operations first (priority)
    is_email_operation = any(keyword in message_lower for keyword in [
        'send email', 'draft email', 'compose email', 'email to', 'write email',
        'sync email', 'check email'
    ])
    
    # Detect explicit navigation requests
    is_navigation = any(keyword in message_lower for keyword in [
        'go to', 'take me to', 'open', 'navigate to', 'switch to'
    ])
    
    # Detect CRM actions (create, delete, update) - ALWAYS use enhanced chatbot for these
    action_verbs = ['create', 'add', 'new', 'delete', 'remove', 'update', 'modify', 'log', 'register', 'make', 'move', 'change', 'set', 'mark', 'complete']
    has_action = any(verb in message_lower for verb in action_verbs)
    
    # Detect explicit data queries (action verb + data type OR modifier + data type)
    query_verbs = ['show', 'list', 'find', 'display', 'view', 'get', 'summarize', 'summary']
    data_types = ['deal', 'deals', 'opportunity', 'opportunities', 'lead', 'leads', 'customer', 'customers', 'contact', 'contacts', 'company', 'companies', 'interaction', 'interactions', 'activity', 'activities', 'task', 'tasks', 'report', 'reports', 'crm', 'information', 'overview', 'pipeline', 'stage', 'status']
    modifiers = ['recent', 'latest', 'top', 'best', 'won', 'lost', 'closing', 'this week', 'today', 'all', 'everything']
    
    has_query_verb = any(verb in message_lower for verb in query_verbs)
    has_data_type = any(dtype in message_lower for dtype in data_types)
    has_modifier = any(mod in message_lower for mod in modifiers)
    
    # Special case: "Company XYZ" or "Contact John" (entity name pattern) should be treated as creation
    # Pattern: starts with entity type followed by capitalized name (not a query verb)
    words = message.split()
    is_entity_name_pattern = (
        len(words) >= 2 and 
        words[0].lower() in ['company', 'contact', 'deal', 'task'] and
        words[1][0].isupper() and 
        not has_query_verb and 
        not has_modifier
    )
    
    # Use enhanced chatbot for: email operations (priority), ALL actions, queries, or navigation
    # Also use for single entity type (just "companies") or entity name patterns ("Company Acme")
    is_crm_operation = (
        is_email_operation or 
        has_action or  # ANY create/delete/update action
        is_entity_name_pattern or  # "Company Acme" pattern
        is_navigation or 
        (has_query_verb and has_data_type) or 
        (has_modifier and has_data_type) or 
        has_query_verb or
        (len(message_lower.split()) == 1 and has_data_type)  # Single word like "companies" (plural only)
    )
    
    if is_crm_operation and not conversation_context:
        # Use enhanced chatbot for CRM queries, actions, and navigation
        response = enhanced_chatbot.process_query(message)
    else:
        # Use basic chatbot for conversations and general questions
        response = chatbot.process_message(message, context=conversation_context)
    
    # Store conversation state if needed
    if response.get('next_step'):
        session['chatbot_state'] = {
            'next_step': response.get('next_step'),
            'pending_email': response.get('pending_email')
        }
    elif response.get('needs_input'):
        # Handle entity creation that needs more input
        needs_input = response.get('needs_input')
        if needs_input == 'entity_type':
            # Chatbot asked what to create
            session['chatbot_state'] = {
                'next_step': 'waiting_for_entity_info',
                'needs_input': needs_input
            }
        elif needs_input in ['company_name', 'contact_name', 'deal_title', 'task_title']:
            # Chatbot asked for specific entity name
            entity_type = needs_input.replace('_name', '').replace('_title', '')
            session['chatbot_state'] = {
                'next_step': 'waiting_for_entity_info',
                'entity_type': entity_type,
                'needs_input': needs_input
            }
    
    # Execute actions based on intent (check both 'action' and 'next_action' for compatibility)
    action = response.get('action') or response.get('next_action')
    
    if action == 'add_customer':
        # Use the extracted data from the chatbot response (already extracted during process_message)
        customer_data = response.get('extracted_data', {})
        
        # If no data in response, extract it (fallback only)
        if not customer_data or not any(customer_data.values()):
            customer_data = chatbot.extract_customer_data(message)
        
        # Validate that we have actual customer information (not just the word "customer")
        has_valid_data = False
        
        # Check for valid name (must exist and be more than just command words)
        if customer_data.get('name'):
            name_lower = customer_data['name'].lower().strip()
            # Name must be at least 2 characters and not be a command word
            if len(name_lower) > 2 and name_lower not in ['customer', 'create', 'add', 'new', 'want', 'to']:
                has_valid_data = True
        
        # Email is always valid if present
        if customer_data.get('email') and '@' in customer_data.get('email'):
            has_valid_data = True
        
        # Company is valid if it's substantial
        if customer_data.get('company'):
            company_lower = customer_data['company'].lower().strip()
            # Must not be a command word or garbage
            invalid_companies = ['customer', 'create', 'add', 'new', 'e a customer', 'a customer', 'want', 'to']
            if company_lower not in invalid_companies and len(company_lower) > 2:
                has_valid_data = True
        
        if has_valid_data:
            try:
                # Ensure name exists for database (required field)
                if not customer_data.get('name'):
                    # If we have email or company but no name, use one of them as name
                    if customer_data.get('email'):
                        customer_data['name'] = customer_data['email'].split('@')[0].replace('.', ' ').title()
                    elif customer_data.get('company'):
                        customer_data['name'] = f"Contact at {customer_data['company']}"
                
                # Add customer to database
                new_customer_id = db.add_customer(customer_data)
                
                # Calculate lead score
                lead_score = lead_scorer.calculate_score(customer_data)
                db.update_customer_score(new_customer_id, lead_score)
                
                # Create workflow
                workflow.create_workflow('new_lead', new_customer_id)
                
                # Update response with success message
                customer_name = customer_data.get('name', customer_data.get('email', customer_data.get('company', 'Customer')))
                response['message'] = f"✓ Customer '{customer_name}' has been successfully created! Lead score: {lead_score:.1f}"
                response['action_executed'] = True
                response['customer_id'] = new_customer_id
                response['customer_data'] = customer_data
            except Exception as e:
                response['message'] = f"I encountered an error creating the customer: {str(e)}. Please try again with more details."
                response['action_executed'] = False
        else:
            # Not enough information, ask for more details
            response['message'] = "To create a customer, I need more details. Please provide the customer's name, email, or company. For example:\n• 'Create a customer named John Doe from Acme Corp'\n• 'Add customer John Smith, email john@example.com'\n• 'New customer from Tech Industries, contact info@tech.com'"
            response['action_executed'] = False
    
    # ==================== SEND EMAIL ACTIONS ====================
    elif action == 'send_email_ask_customer':
        # Step 1: Ask for customer name
        response['message'] = "Sure! What is the name of the customer you'd like to email?"
        response['action_executed'] = False
        response['next_step'] = 'waiting_for_customer_name'
    
    elif action == 'send_email_lookup_customer':
        # Step 2: Look up customer by name
        customer_name = response.get('extracted_data', {}).get('customer_name')
        
        if customer_name:
            try:
                # Search for customer by name
                customers = db.get_all_customers()
                matching_customers = [c for c in customers if customer_name.lower() in c.get('name', '').lower()]
                
                if matching_customers:
                    customer = matching_customers[0]
                    customer_email = customer.get('email')
                    
                    if customer_email:
                        response['message'] = f"Found {customer['name']} ({customer_email}). What would you like to say in the email?"
                        response['action_executed'] = False
                        response['next_step'] = 'waiting_for_email_body'
                        response['pending_email'] = {
                            'customer_id': customer['id'],
                            'customer_name': customer['name'],
                            'recipient': customer_email,
                            'subject': 'CRM Email'
                        }
                    else:
                        response['message'] = f"Found {customer['name']}, but they don't have an email address on file. Please add their email first."
                        response['action_executed'] = False
                else:
                    response['message'] = f"I couldn't find a customer named '{customer_name}'. Please check the name and try again, or create the customer first."
                    response['action_executed'] = False
            except Exception as e:
                response['message'] = f"Error looking up customer: {str(e)}"
                response['action_executed'] = False
        else:
            response['message'] = "Please provide the customer's name."
            response['action_executed'] = False
    
    elif action == 'delete_customer_ask_name':
        # User wants to delete a customer but didn't provide a name
        response['message'] = "Which customer would you like to delete? Please provide their name."
        response['action_executed'] = False
        response['next_step'] = 'waiting_for_delete_customer_name'
        
        # Store session state
        session['chatbot_state'] = {
            'next_step': 'waiting_for_delete_customer_name'
        }
    
    elif action == 'delete_customer_lookup':
        # User wants to delete a specific customer
        customer_name = response.get('extracted_data', {}).get('customer_name')
        
        if customer_name:
            try:
                # Search for customer by name
                customers = db.get_all_customers()
                matching_customers = [c for c in customers if customer_name.lower() in c.get('name', '').lower()]
                
                if matching_customers:
                    customer = matching_customers[0]
                    
                    response['message'] = f"Are you sure you want to delete {customer['name']} (ID: {customer['id']})? Type 'yes' to confirm or 'no' to cancel."
                    response['action_executed'] = False
                    response['next_step'] = 'waiting_for_delete_confirmation'
                    response['pending_delete'] = {
                        'customer_id': customer['id'],
                        'customer_name': customer['name']
                    }
                    
                    # Store session state
                    session['chatbot_state'] = {
                        'next_step': 'waiting_for_delete_confirmation',
                        'pending_delete': {
                            'customer_id': customer['id'],
                            'customer_name': customer['name']
                        }
                    }
                else:
                    response['message'] = f"I couldn't find a customer named '{customer_name}'. Please check the name and try again."
                    response['action_executed'] = False
            except Exception as e:
                response['message'] = f"Error looking up customer: {str(e)}"
                response['action_executed'] = False
        else:
            response['message'] = "Please provide the customer's name to delete."
            response['action_executed'] = False
    
    elif action == 'send_email':
        email_data = response.get('extracted_data', {})
        recipient = email_data.get('recipient')
        
        if recipient:
            try:
                # For demo purposes, log the email action
                # In production, integrate with actual email service (SendGrid, AWS SES, etc.)
                email_log = {
                    'recipient': recipient,
                    'subject': email_data.get('subject', 'CRM Email'),
                    'body': email_data.get('body', message),
                    'sent_at': datetime.now().isoformat()
                }
                
                response['message'] = f"✓ Email sent to {recipient}!"
                response['action_executed'] = True
                response['email_data'] = email_log
                
                # Log as interaction
                if customer_id:
                    db.add_interaction({
                        'customer_id': customer_id,
                        'type': 'email',
                        'channel': 'email',
                        'notes': f"Sent email: {email_data.get('subject', 'Message from CRM')}"
                    })
            except Exception as e:
                response['message'] = f"Failed to send email: {str(e)}"
                response['action_executed'] = False
        else:
            response['message'] = "Please specify who to send the email to. For example: 'Send email to john@example.com' or 'Email customer John Doe'"
            response['action_executed'] = False
    
    # ==================== GET INSIGHTS ACTION ====================
    elif action == 'get_insights':
        try:
            # Get various insights from database
            insights = {
                'total_customers': len(db.get_all_customers()),
                'recent_interactions': len(db.get_recent_interactions(limit=10)),
                'top_leads': db.get_top_leads(limit=5)
            }
            
            # Use AI to generate natural language summary
            insight_prompt = f"""Summarize these CRM insights in 2-3 sentences:
- Total customers: {insights['total_customers']}
- Recent interactions: {insights['recent_interactions']}
- Top leads: {len(insights['top_leads'])} high-value prospects

Provide a brief, professional summary."""
            
            ai_summary = ai_model.generate(insight_prompt, max_length=250)
            
            response['message'] = ai_summary
            response['action_executed'] = True
            response['insights_data'] = insights
        except Exception as e:
            response['message'] = f"Here's what I found: {insights.get('total_customers', 0)} total customers with {insights.get('recent_interactions', 0)} recent interactions."
            response['action_executed'] = True
            response['insights_data'] = insights
    
    # Log interaction if customer_id provided
    if customer_id:
        db.add_interaction({
            'customer_id': customer_id,
            'type': 'chatbot',
            'channel': 'web',
            'notes': f"User: {message}\nBot: {response.get('message', '')}"
        })
    
    return jsonify(response)

@app.route('/api/ai/analyze-lead', methods=['POST', 'OPTIONS'])
def analyze_lead():
    """AI lead analysis endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    customer_id = data.get('customer_id')
    
    if not customer_id:
        return jsonify({'error': 'customer_id required'}), 400
    
    customer = db.get_customer(customer_id)
    interactions = db.get_customer_interactions(customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Get AI insights
    insights = ai_services.generate_customer_insights(customer)
    
    return jsonify(insights)

@app.route('/api/opportunities', methods=['GET', 'POST', 'OPTIONS'])
def manage_opportunities():
    """Opportunities management endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    if request.method == 'GET':
        customer_id = request.args.get('customer_id')
        if customer_id:
            opportunities = db.get_customer_opportunities(int(customer_id))
        else:
            opportunities = db.get_all_opportunities()
        return jsonify(opportunities)
    
    elif request.method == 'POST':
        data = request.get_json()
        opportunity_id = db.add_opportunity(data)
        return jsonify({'success': True, 'opportunity_id': opportunity_id})

@app.route('/api/reports/sales', methods=['GET', 'OPTIONS'])
def sales_report():
    """Enhanced sales report endpoint with accurate metrics from deals table"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.db_helper import get_db
        conn = get_db()
        cursor = conn.cursor()
        
        customers = db.get_all_customers()
        interactions = db.get_all_interactions()
        
        # Get deal-based metrics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_deals,
                SUM(CASE WHEN stage = 'Closed Won' THEN 1 ELSE 0 END) as won_deals,
                SUM(CASE WHEN stage = 'Closed Lost' THEN 1 ELSE 0 END) as lost_deals,
                SUM(CASE WHEN stage = 'Closed Won' THEN value ELSE 0 END) as total_revenue,
                SUM(CASE WHEN stage NOT IN ('Closed Won', 'Closed Lost') THEN value ELSE 0 END) as pipeline_value,
                AVG(CASE WHEN stage = 'Closed Won' THEN value ELSE NULL END) as avg_deal_size
            FROM deals
        ''')
        
        deal_stats = cursor.fetchone()
        total_deals = deal_stats[0] or 0
        won_deals = deal_stats[1] or 0
        lost_deals = deal_stats[2] or 0
        total_revenue = deal_stats[3] or 0
        pipeline_value = deal_stats[4] or 0
        avg_deal_size = deal_stats[5] or 0
        
        # Calculate metrics
        total_customers = len(customers)
        total_opportunities = won_deals + lost_deals
        conversion_rate = (won_deals / total_deals * 100) if total_deals > 0 else 0
        win_rate = (won_deals / total_opportunities * 100) if total_opportunities > 0 else 0
        
        # Get deals by stage for conversion funnel
        cursor.execute('''
            SELECT stage, COUNT(*) as count, SUM(value) as total_value
            FROM deals
            GROUP BY stage
        ''')
        
        stage_data = {}
        for row in cursor.fetchall():
            stage_data[row[0]] = {'count': row[1], 'value': row[2] or 0}
    
        
        # Conversion funnel from deal stages
        conversion_funnel = {
            'leads': stage_data.get('Lead', {}).get('count', 0),
            'qualified': stage_data.get('Qualified', {}).get('count', 0),
            'proposal': stage_data.get('Proposal', {}).get('count', 0),
            'negotiation': stage_data.get('Negotiation', {}).get('count', 0),
            'closed': won_deals,
            'lost': lost_deals
        }
        
        # Group customers by status
        customers_by_status = {}
        for customer in customers:
            status = customer.get('status', 'unknown')
            customers_by_status[status] = customers_by_status.get(status, 0) + 1
        
        customers_by_status_array = [
            {'status': status, 'count': count} 
            for status, count in customers_by_status.items()
        ]
        
        # Revenue by industry from companies
        cursor.execute('''
            SELECT c.industry, SUM(d.value) as total_revenue
            FROM deals d
            JOIN companies c ON d.company_id = c.id
            WHERE d.stage = 'Closed Won'
            GROUP BY c.industry
        ''')
        
        revenue_by_industry_array = [
            {'industry': row[0] or 'Other', 'total_revenue': row[1] or 0}
            for row in cursor.fetchall()
        ]
        
        # Interaction metrics
        total_interactions = len(interactions)
        interactions_by_type = {}
        for interaction in interactions:
            itype = interaction.get('type', 'other')
            interactions_by_type[itype] = interactions_by_type.get(itype, 0) + 1
        
        interactions_by_type_array = [
            {'type': itype, 'count': count}
            for itype, count in interactions_by_type.items()
        ]
        
        avg_interactions_per_customer = total_interactions / total_customers if total_customers > 0 else 0
        
        report = {
            'total_revenue': round(total_revenue, 2),
            'pipeline_value': round(pipeline_value, 2),
            'total_customers': total_customers,
            'converted_customers': won_deals,
            'active_leads': total_deals - won_deals - lost_deals,
            'conversion_rate': round(conversion_rate, 1),
            'win_rate': round(win_rate, 1),
            'avg_deal_size': round(avg_deal_size, 2),
            'customers_by_status': customers_by_status_array,
            'revenue_by_industry': revenue_by_industry_array,
            'conversion_funnel': conversion_funnel,
            'total_interactions': total_interactions,
            'interactions_by_type': interactions_by_type_array,
            'avg_interactions_per_customer': round(avg_interactions_per_customer, 1),
            'monthly_revenue': round(total_revenue, 2),
            'monthly_customers': won_deals
        }
    except Exception as e:
        print(f"Sales report error: {e}")
        # Fallback to basic metrics
        customers = db.get_all_customers()
        report = {
            'total_revenue': 0,
            'pipeline_value': 0,
            'total_customers': len(customers),
            'converted_customers': 0,
            'active_leads': 0,
            'conversion_rate': 0,
            'win_rate': 0,
            'avg_deal_size': 0,
            'customers_by_status': [],
            'revenue_by_industry': [],
            'conversion_funnel': {},
            'total_interactions': 0,
            'interactions_by_type': [],
            'avg_interactions_per_customer': 0,
            'monthly_revenue': 0,
            'monthly_customers': 0
        }
    
    return jsonify(report)

# ==================== AI-POWERED FEATURES ROUTES ====================

@app.route('/api/ai/predict-deal-success', methods=['POST', 'OPTIONS'])
def predict_deal_success():
    """Predict deal success probability"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        deal_id = data.get('deal_id')
        
        if not deal_id:
            return jsonify({'error': 'deal_id is required'}), 400
        
        prediction = predictive_insights.predict_deal_success(deal_id)
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/predict-churn', methods=['POST', 'OPTIONS'])
def predict_churn():
    """Predict customer churn risk"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        customer_id = data.get('customer_id')  # Legacy support
        
        if not contact_id and not customer_id:
            return jsonify({'error': 'contact_id or customer_id is required'}), 400
        
        prediction = predictive_insights.predict_churn_risk(
            customer_id=customer_id,
            contact_id=contact_id
        )
        return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/batch-predict-deals', methods=['GET', 'OPTIONS'])
def batch_predict_deals():
    """Get predictions for all active deals"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        predictions = predictive_insights.batch_predict_deal_success()
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/batch-predict-churn', methods=['GET', 'OPTIONS'])
def batch_predict_churn():
    """Get churn predictions for all contacts"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        predictions = predictive_insights.batch_predict_churn()
        return jsonify({
            'success': True,
            'count': len(predictions),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/smart-reminders', methods=['GET', 'OPTIONS'])
def get_smart_reminders():
    """Get smart reminders for quiet leads and stalled deals"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        reminders = smart_automation.generate_smart_reminders()
        return jsonify({
            'success': True,
            'count': len(reminders),
            'reminders': reminders
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/auto-generate-task', methods=['POST', 'OPTIONS'])
def auto_generate_task():
    """Auto-generate follow-up task after activity"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        activity_id = data.get('activity_id')
        
        if not activity_id:
            return jsonify({'error': 'activity_id is required'}), 400
        
        result = smart_automation.auto_generate_follow_up_tasks(activity_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/enrich-contact', methods=['POST', 'OPTIONS'])
def enrich_contact():
    """Enrich contact data with AI"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        auto_save = data.get('auto_save', True)
        
        if not contact_id:
            return jsonify({'error': 'contact_id is required'}), 400
        
        result = smart_automation.enrich_contact_data(contact_id, auto_save)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/auto-log-activity', methods=['POST', 'OPTIONS'])
def auto_log_activity():
    """Auto-log activity and generate follow-up task"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        activity_type = data.get('type')
        contact_id = data.get('contact_id')
        company_id = data.get('company_id')
        deal_id = data.get('deal_id')
        notes = data.get('notes', '')
        
        if not activity_type:
            return jsonify({'error': 'type is required'}), 400
        
        result = smart_automation.auto_log_activity(
            activity_type, contact_id, company_id, deal_id, notes
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/chatbot-query', methods=['POST', 'OPTIONS'])
def chatbot_query():
    """Enhanced chatbot with CRM query capabilities"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_context = data.get('context')
        
        if not message:
            return jsonify({'error': 'message is required'}), 400
        
        response = enhanced_chatbot.process_query(message, user_context)
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/generate-email', methods=['POST', 'OPTIONS'])
def generate_email():
    """Generate AI-powered email draft"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        contact_id = data.get('contact_id')
        purpose = data.get('purpose', 'follow-up')
        
        # Get customer/contact data
        if contact_id:
            from modules.db_helper import get_db
            db_conn = get_db()
            cursor = db_conn.cursor()
            cursor.execute('''
                SELECT c.*, comp.name as company_name 
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                WHERE c.id = ?
            ''', (contact_id,))
            customer_data = dict(cursor.fetchone() or {})
            customer_data['name'] = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        elif customer_id:
            customer_data = db.get_customer(customer_id)
        else:
            return jsonify({'error': 'customer_id or contact_id is required'}), 400
        
        if not customer_data:
            return jsonify({'error': 'Customer/Contact not found'}), 404
        
        email_content = ai_services.generate_email_template(customer_data, purpose)
        
        return jsonify({
            'success': True,
            'email_content': email_content,
            'purpose': purpose
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analyze-sentiment', methods=['POST', 'OPTIONS'])
def analyze_sentiment():
    """Analyze sentiment of text"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'text is required'}), 400
        
        result = ai_services.analyze_sentiment(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/generate-pitch', methods=['POST', 'OPTIONS'])
def generate_pitch():
    """Generate sales pitch"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        contact_id = data.get('contact_id')
        product_info = data.get('product_info', '')
        
        # Get customer/contact data
        if contact_id:
            from modules.db_helper import get_db
            db_conn = get_db()
            cursor = db_conn.cursor()
            cursor.execute('''
                SELECT c.*, comp.name as company_name, comp.industry
                FROM contacts c
                LEFT JOIN companies comp ON c.company_id = comp.id
                WHERE c.id = ?
            ''', (contact_id,))
            customer_data = dict(cursor.fetchone() or {})
            customer_data['name'] = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()
        elif customer_id:
            customer_data = db.get_customer(customer_id)
        else:
            return jsonify({'error': 'customer_id or contact_id is required'}), 400
        
        if not customer_data:
            return jsonify({'error': 'Customer/Contact not found'}), 404
        
        pitch = ai_services.generate_sales_pitch(customer_data, product_info)
        
        return jsonify({
            'success': True,
            'pitch': pitch
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== AI AUTOMATION ROUTES ====================

@app.route('/api/ai/draft-email', methods=['POST', 'OPTIONS'])
@cross_origin()
def draft_email():
    """Draft an email with AI assistance"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_automation import EmailAutomation
        email_auto = EmailAutomation()
        
        data = request.json
        context = data.get('context', '')
        tone = data.get('tone', 'professional')
        purpose = data.get('purpose', 'follow_up')
        recipient_info = data.get('recipient_info', {})
        
        result = email_auto.draft_email(context, tone, purpose, recipient_info)
        
        return jsonify({
            'success': True,
            'email': result
        })
    except Exception as e:
        print(f"Error drafting email: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/enrich-company', methods=['POST', 'OPTIONS'])
@cross_origin()
def enrich_company():
    """Enrich company data with external information"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.data_enrichment import DataEnrichment
        enrichment = DataEnrichment()
        
        data = request.json
        company_name = data.get('company_name')
        company_id = data.get('company_id')
        
        if not company_name and not company_id:
            return jsonify({'error': 'company_name or company_id required'}), 400
        
        # Get company from DB if ID provided
        if company_id:
            from modules.db_helper import get_db
            db_conn = get_db()
            cursor = db_conn.cursor()
            cursor.execute('SELECT name FROM customers WHERE id = ?', (company_id,))
            row = cursor.fetchone()
            if row:
                company_name = row[0]
        
        if not company_name:
            return jsonify({'error': 'Company not found'}), 404
        
        result = enrichment.enrich_company(company_name)
        
        # Update company in database if ID provided
        if company_id and result.get('success'):
            from modules.db_helper import get_db
            db_conn = get_db()
            cursor = db_conn.cursor()
            
            update_fields = []
            if result.get('industry'):
                update_fields.append(f"industry = '{result['industry']}'")
            if result.get('website'):
                update_fields.append(f"website = '{result['website']}'")
            if result.get('description'):
                update_fields.append(f"notes = '{result['description']}'")
            
            if update_fields:
                cursor.execute(f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?", (company_id,))
                db_conn.commit()
        
        return jsonify(result)
    except Exception as e:
        print(f"Error enriching company: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/execute-action', methods=['POST', 'OPTIONS'])
@cross_origin()
def execute_action():
    """Execute a CRM action via AI"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.ai_actions import AIActions
        ai_actions = AIActions()
        
        data = request.json
        action_type = data.get('action_type')
        action_data = data.get('data', {})
        user_id = session.get('user_id', 1)
        
        result = ai_actions.execute_action(action_type, action_data, user_id)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error executing action: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/analytics/conversational', methods=['POST', 'OPTIONS'])
@cross_origin()
def conversational_analytics():
    """Get analytics via natural language query"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.ai_chatbot_enhanced import EnhancedChatbot
        from modules.groq_ai import GroqAI
        
        groq_ai = GroqAI()
        chatbot = EnhancedChatbot(groq_ai)
        
        data = request.json
        query = data.get('query', '')
        
        result = chatbot.process_query(query)
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in conversational analytics: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/auto-generate', methods=['POST', 'OPTIONS'])
@cross_origin()
def auto_generate_tasks():
    """Auto-generate follow-up tasks"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.ai_actions import AIActions
        ai_actions = AIActions()
        
        data = request.json
        interaction_id = data.get('interaction_id')
        interaction_type = data.get('interaction_type', 'call')
        customer_id = data.get('customer_id')
        deal_id = data.get('deal_id')
        notes = data.get('notes', '')
        user_id = session.get('user_id', 1)
        
        tasks = ai_actions.auto_generate_tasks(
            interaction_type=interaction_type,
            customer_id=customer_id,
            deal_id=deal_id,
            notes=notes,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'tasks': tasks
        })
    except Exception as e:
        print(f"Error auto-generating tasks: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ==================== EMAIL INTEGRATION ROUTES ====================

@app.route('/api/email/accounts', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def manage_email_accounts():
    """Manage email accounts"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        user_id = session.get('user_id', 1)
        
        if request.method == 'GET':
            # Get all email accounts for user
            cursor = email_integration.db.cursor()
            cursor.execute("""
                SELECT id, email_address, provider, display_name, is_primary, 
                       is_active, last_sync, sync_enabled, auto_log_interactions
                FROM email_accounts 
                WHERE user_id = ?
                ORDER BY is_primary DESC, created_at DESC
            """, (user_id,))
            
            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'id': row[0],
                    'email_address': row[1],
                    'provider': row[2],
                    'display_name': row[3],
                    'is_primary': bool(row[4]),
                    'is_active': bool(row[5]),
                    'last_sync': row[6],
                    'sync_enabled': bool(row[7]),
                    'auto_log_interactions': bool(row[8])
                })
            
            return jsonify({
                'success': True,
                'accounts': accounts
            })
        
        elif request.method == 'POST':
            # Add new email account
            data = request.json
            result = email_integration.add_email_account(
                user_id=user_id,
                email_address=data.get('email_address'),
                provider=data.get('provider'),
                password=data.get('password'),
                display_name=data.get('display_name')
            )
            return jsonify(result)
    
    except Exception as e:
        print(f"Error managing email accounts: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/sync/<int:account_id>', methods=['POST', 'OPTIONS'])
@cross_origin()
def sync_emails(account_id):
    """Sync emails from provider"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        
        data = request.json or {}
        days_back = data.get('days_back', 7)
        auto_log = data.get('auto_log', True)
        
        result = email_integration.sync_emails(account_id, days_back, auto_log)
        return jsonify(result)
    
    except Exception as e:
        print(f"Error syncing emails: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/send', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_email():
    """Send email from CRM"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        
        data = request.json
        account_id = data.get('account_id')
        
        # If no account specified, use primary
        if not account_id:
            user_id = session.get('user_id', 1)
            cursor = email_integration.db.cursor()
            cursor.execute("""
                SELECT id FROM email_accounts 
                WHERE user_id = ? AND is_primary = 1 AND is_active = 1
                LIMIT 1
            """, (user_id,))
            account = cursor.fetchone()
            if account:
                account_id = account[0]
            else:
                return jsonify({
                    'success': False,
                    'error': 'No email account configured'
                }), 400
        
        result = email_integration.send_email(
            account_id=account_id,
            to_email=data.get('to_email'),
            subject=data.get('subject'),
            body=data.get('body'),
            customer_id=data.get('customer_id'),
            cc=data.get('cc'),
            template_id=data.get('template_id')
        )
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/templates', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def manage_email_templates():
    """Manage email templates"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        user_id = session.get('user_id', 1)
        
        if request.method == 'GET':
            category = request.args.get('category')
            templates = email_integration.get_templates(user_id, category)
            
            return jsonify({
                'success': True,
                'templates': templates
            })
        
        elif request.method == 'POST':
            data = request.json
            result = email_integration.save_template(
                user_id=user_id,
                name=data.get('name'),
                subject=data.get('subject'),
                body=data.get('body'),
                category=data.get('category', 'general'),
                variables=data.get('variables', [])
            )
            
            return jsonify(result)
    
    except Exception as e:
        print(f"Error managing templates: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/templates/<int:template_id>/apply', methods=['POST', 'OPTIONS'])
@cross_origin()
def apply_email_template(template_id):
    """Apply variables to email template"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        
        data = request.json
        variables = data.get('variables', {})
        
        result = email_integration.apply_template(template_id, variables)
        return jsonify(result)
    
    except Exception as e:
        print(f"Error applying template: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/email/synced', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_synced_emails():
    """Get synced emails"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        from modules.email_integration import EmailIntegration
        email_integration = EmailIntegration()
        user_id = session.get('user_id', 1)
        
        limit = int(request.args.get('limit', 50))
        customer_id = request.args.get('customer_id')
        
        cursor = email_integration.db.cursor()
        
        query = """
            SELECT e.id, e.subject, e.from_email, e.to_email, e.sent_date, 
                   e.body_preview, e.is_sent, e.customer_id, c.name as customer_name
            FROM email_sync_log e
            LEFT JOIN customers c ON e.customer_id = c.id
            WHERE e.account_id IN (
                SELECT id FROM email_accounts WHERE user_id = ?
            )
        """
        params = [user_id]
        
        if customer_id:
            query += " AND e.customer_id = ?"
            params.append(customer_id)
        
        query += " ORDER BY e.sent_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        emails = []
        for row in cursor.fetchall():
            emails.append({
                'id': row[0],
                'subject': row[1],
                'from_email': row[2],
                'to_email': row[3],
                'sent_date': row[4],
                'body_preview': row[5],
                'is_sent': bool(row[6]),
                'customer_id': row[7],
                'customer_name': row[8]
            })
        
        return jsonify({
            'success': True,
            'emails': emails
        })
    
    except Exception as e:
        print(f"Error getting synced emails: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-email', methods=['POST', 'OPTIONS'])
@cross_origin()
def send_email_chatbot():
    """Send email from chatbot and log to interactions"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.get_json()
        to_email = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        contact_id = data.get('contact_id')
        user_id = data.get('user_id', 1)
        
        if not all([to_email, subject, body]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Clean and normalize the email
        to_email = to_email.strip().lower()
        
        # Get database connection
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Find contact by email - REQUIRED (case-insensitive)
        # Check both customers and contacts tables
        if not contact_id and to_email:
            # First try customers table
            cursor.execute("SELECT id, name, email FROM customers WHERE LOWER(TRIM(email)) = ?", (to_email,))
            result = cursor.fetchone()
            if result:
                contact_id = result[0]
                print(f"📧 Found contact in customers: {result[1]} (ID: {contact_id}) with email: {result[2]}")
            else:
                # Try contacts table
                cursor.execute("SELECT id, first_name || ' ' || last_name as name, email FROM contacts WHERE LOWER(TRIM(email)) = ?", (to_email,))
                result = cursor.fetchone()
                if result:
                    contact_id = result[0]
                    print(f"📧 Found contact in contacts: {result[1]} (ID: {contact_id}) with email: {result[2]}")
        
        # Contact is required - cannot send email without a contact
        if not contact_id:
            # Show available contacts for debugging from both tables
            cursor.execute("SELECT name, email FROM customers WHERE email IS NOT NULL AND email != '' LIMIT 5")
            customers_available = cursor.fetchall()
            cursor.execute("SELECT first_name || ' ' || last_name, email FROM contacts WHERE email IS NOT NULL AND email != '' LIMIT 5")
            contacts_available = cursor.fetchall()
            
            available = customers_available + contacts_available
            available_emails = [f"{row[0]} ({row[1]})" for row in available] if available else ["No contacts with emails found"]
            
            return jsonify({
                'success': False, 
                'message': f'No contact found with email "{to_email}". Please add this email to your contacts first.',
                'available_contacts': available_emails
            }), 400
        
        # Log email to interactions table (now contact_id is guaranteed to exist)
        cursor.execute('''
            INSERT INTO interactions (customer_id, type, channel, notes, created_at, user_id)
            VALUES (?, ?, ?, ?, datetime('now'), ?)
        ''', (
            contact_id,
            'email',
            'email',
            f"Subject: {subject}\n\nTo: {to_email}\n\n{body}"
        , user_id))
        
        conn.commit()
        interaction_id = cursor.lastrowid
        
        # Send email via SendGrid
        email_sent = False
        sendgrid_error = None
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
            import os
            
            sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
            from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@yourcompany.com')
            from_name = os.getenv('SENDGRID_FROM_NAME', 'Lead Mind')
            
            if sendgrid_api_key and sendgrid_api_key != 'your_sendgrid_api_key_here':
                # Create SendGrid message
                message = Mail(
                    from_email=Email(from_email, from_name),
                    to_emails=To(to_email),
                    subject=subject,
                    plain_text_content=Content("text/plain", body)
                )
                
                # Send email
                sg = SendGridAPIClient(sendgrid_api_key)
                response = sg.send(message)
                
                if response.status_code in [200, 202]:
                    email_sent = True
                    print(f"✅ Email sent via SendGrid to {to_email}: {subject}")
                else:
                    sendgrid_error = f"SendGrid returned status {response.status_code}"
                    print(f"⚠️ SendGrid error: {sendgrid_error}")
            else:
                print(f"⚠️ SendGrid not configured. Email logged but not sent.")
                print(f"   To: {to_email}")
                print(f"   Subject: {subject}")
                print(f"   Body: {body[:100]}...")
                
        except Exception as email_error:
            sendgrid_error = str(email_error)
            print(f"❌ Failed to send email via SendGrid: {sendgrid_error}")
        
        print(f"📝 Email logged as interaction #{interaction_id}")
        
        return jsonify({
            'success': True,
            'message': 'Email sent successfully' if email_sent else 'Email logged (SendGrid not configured)',
            'email_sent': email_sent,
            'interaction_id': interaction_id,
            'contact_id': contact_id,
            'sendgrid_error': sendgrid_error
        })
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== ENHANCED CRM ROUTES ====================
# Import and setup enhanced routes
from api_routes_enhanced import setup_enhanced_routes
setup_enhanced_routes(app, db_enhanced, db, auth)

if __name__ == '__main__':
    # Start workflow scheduler
    workflow.start_scheduler()
    
    # Run the application
    app.run(debug=False, host='0.0.0.0', port=5000)  # Disabled debug to prevent auto-restart issues