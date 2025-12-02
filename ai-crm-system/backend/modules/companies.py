"""
Companies Management Module
Handles company CRUD operations
"""

from flask import Blueprint, request, jsonify, session
from .db_helper import get_db
from functools import wraps
import sqlite3

companies_bp = Blueprint('companies', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@companies_bp.route('/api/companies', methods=['GET'])
@login_required
def get_companies():
    """Get all companies with optional filtering"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get query parameters for filtering
        search = request.args.get('search', '')
        industry = request.args.get('industry', '')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = '''
            SELECT c.*, u.username as created_by_name,
                   COUNT(DISTINCT cust.id) as customer_count,
                   COUNT(DISTINCT opp.id) as opportunity_count
            FROM companies c
            LEFT JOIN users u ON c.assigned_to = u.id
            LEFT JOIN customers cust ON cust.company_id = c.id
            LEFT JOIN opportunities opp ON opp.company_id = c.id
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ' AND (c.name LIKE ? OR c.email LIKE ? OR c.website LIKE ?)'
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if industry:
            query += ' AND c.industry = ?'
            params.append(industry)
        
        query += ' GROUP BY c.id ORDER BY c.created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        companies = []
        for row in cursor.fetchall():
            companies.append({
                'id': row[0],
                'name': row[1],
                'industry': row[2],
                'website': row[3],
                'phone': row[4],
                'email': row[5],
                'address': row[6],
                'city': row[7],
                'state': row[8],
                'country': row[9],
                'postal_code': row[10],
                'employee_count': row[11],
                'annual_revenue': row[12],
                'description': row[13],
                'logo_url': row[14],
                'created_at': row[15],
                'updated_at': row[16],
                'created_by': row[17],
                'created_by_name': row[18],
                'customer_count': row[19],
                'opportunity_count': row[20]
            })
        
        return jsonify({'success': True, 'companies': companies})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@companies_bp.route('/api/companies/<int:company_id>', methods=['GET'])
@login_required
def get_company(company_id):
    """Get a specific company with details"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Get company details
        cursor.execute('''
            SELECT c.*, u.username as created_by_name
            FROM companies c
            LEFT JOIN users u ON c.assigned_to = u.id
            WHERE c.id = ?
        ''', (company_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'message': 'Company not found'}), 404
        
        company = {
            'id': row[0],
            'name': row[1],
            'industry': row[2],
            'website': row[3],
            'phone': row[4],
            'email': row[5],
            'address': row[6],
            'city': row[7],
            'state': row[8],
            'country': row[9],
            'postal_code': row[10],
            'employee_count': row[11],
            'annual_revenue': row[12],
            'description': row[13],
            'logo_url': row[14],
            'created_at': row[15],
            'updated_at': row[16],
            'created_by': row[17],
            'created_by_name': row[18]
        }
        
        # Get associated customers
        cursor.execute('''
            SELECT id, name, email, phone, status
            FROM customers
            WHERE company_id = ?
            ORDER BY created_at DESC
        ''', (company_id,))
        
        company['customers'] = []
        for row in cursor.fetchall():
            company['customers'].append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'status': row[4]
            })
        
        # Get associated opportunities
        cursor.execute('''
            SELECT id, name, value, deal_stage, probability, expected_close_date
            FROM opportunities
            WHERE company_id = ?
            ORDER BY created_at DESC
        ''', (company_id,))
        
        company['opportunities'] = []
        for row in cursor.fetchall():
            company['opportunities'].append({
                'id': row[0],
                'name': row[1],
                'value': row[2],
                'deal_stage': row[3],
                'probability': row[4],
                'expected_close_date': row[5]
            })
        
        return jsonify({'success': True, 'company': company})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@companies_bp.route('/api/companies', methods=['POST'])
@login_required
def create_company():
    """Create a new company"""
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            INSERT INTO companies (
                name, industry, website, phone, email, address,
                city, state, country, postal_code, description, assigned_to
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('industry'),
            data.get('website'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            data.get('city'),
            data.get('state'),
            data.get('country'),
            data.get('postal_code'),
            data.get('description'),
            session['user_id']
        ))
        
        company_id = cursor.lastrowid
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Company created successfully',
            'company_id': company_id
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@companies_bp.route('/api/companies/<int:company_id>', methods=['PUT'])
@login_required
def update_company(company_id):
    """Update a company"""
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            UPDATE companies SET
                name = ?, industry = ?, website = ?, phone = ?,
                email = ?, address = ?, city = ?, state = ?,
                country = ?, postal_code = ?, description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('name'),
            data.get('industry'),
            data.get('website'),
            data.get('phone'),
            data.get('email'),
            data.get('address'),
            data.get('city'),
            data.get('state'),
            data.get('country'),
            data.get('postal_code'),
            data.get('description'),
            company_id
        ))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Company updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@companies_bp.route('/api/companies/<int:company_id>', methods=['DELETE'])
@login_required
def delete_company(company_id):
    """Delete a company"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Check if company has associated customers or opportunities
        cursor.execute('SELECT COUNT(*) FROM customers WHERE company_id = ?', (company_id,))
        customer_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM opportunities WHERE company_id = ?', (company_id,))
        opportunity_count = cursor.fetchone()[0]
        
        if customer_count > 0 or opportunity_count > 0:
            return jsonify({
                'success': False,
                'message': f'Cannot delete company with {customer_count} customers and {opportunity_count} opportunities'
            }), 400
        
        cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Company deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@companies_bp.route('/api/companies/industries', methods=['GET'])
@login_required
def get_industries():
    """Get list of all industries"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT DISTINCT industry, COUNT(*) as count
            FROM companies
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry
            ORDER BY count DESC
        ''')
        
        industries = []
        for row in cursor.fetchall():
            industries.append({
                'name': row[0],
                'count': row[1]
            })
        
        return jsonify({'success': True, 'industries': industries})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
