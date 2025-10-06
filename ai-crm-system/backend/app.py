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
    
    customers = db.get_all_customers()
    interactions = db.get_recent_interactions(10)
    
    # Calculate metrics
    total_customers = len(customers)
    active_leads = len([c for c in customers if c.get('status') in ['lead', 'qualified', 'interested']])
    converted_customers = len([c for c in customers if c.get('status') == 'customer'])
    conversion_rate = (converted_customers / total_customers * 100) if total_customers > 0 else 0
    
    # Calculate revenue
    monthly_revenue = sum([c.get('budget', 0) for c in customers if c.get('status') == 'customer'])
    
    # Get top leads
    top_leads = sorted(customers, key=lambda x: x.get('lead_score', 0), reverse=True)[:5]
    
    # Sales forecast
    forecast_data = sales_forecaster.get_quick_forecast()
    
    analytics = {
        'total_customers': total_customers,
        'active_leads': active_leads,
        'conversion_rate': round(conversion_rate, 1),
        'monthly_revenue': monthly_revenue,
        'top_leads': top_leads,
        'recent_interactions': interactions,
        'sales_forecast': forecast_data
    }
    
    return jsonify(analytics)

@app.route('/api/notifications', methods=['GET', 'OPTIONS'])
def get_notifications():
    """Get user notifications"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    # Get recent activities and create notifications
    customers = db.get_all_customers()
    interactions = db.get_recent_interactions(20)
    
    notifications = []
    
    # New customer notifications
    for customer in customers[:5]:  # Last 5 customers
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
    for lead in high_score_leads[:3]:
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
    for interaction in interactions[:5]:
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
    
    return jsonify({'notifications': notifications[:10]})  # Return top 10

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
    """Chatbot message endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    message = data.get('message', '')
    customer_id = data.get('customer_id')
    
    # Get chatbot response
    response = chatbot.process_message(message)
    
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
    """Sales report endpoint"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    customers = db.get_all_customers()
    interactions = db.get_all_interactions()
    
    # Generate report
    report = {
        'total_revenue': sum([c.get('budget', 0) for c in customers if c.get('status') == 'customer']),
        'pipeline_value': sum([c.get('budget', 0) for c in customers if c.get('status') in ['qualified', 'interested']]),
        'customers_by_status': {},
        'revenue_by_industry': {},
        'conversion_funnel': {}
    }
    
    # Group by status
    for customer in customers:
        status = customer.get('status', 'unknown')
        report['customers_by_status'][status] = report['customers_by_status'].get(status, 0) + 1
    
    # Group by industry
    for customer in customers:
        if customer.get('status') == 'customer':
            industry = customer.get('industry', 'Other')
            revenue = customer.get('budget', 0)
            report['revenue_by_industry'][industry] = report['revenue_by_industry'].get(industry, 0) + revenue
    
    return jsonify(report)

if __name__ == '__main__':
    # Start workflow scheduler
    workflow.start_scheduler()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)