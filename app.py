from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import DatabaseManager
from config import Config
import psycopg2

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = Config.SECRET_KEY

db_manager = None

try:
    db_manager = DatabaseManager()
    print("✓ Database connection established successfully")
    print("✓ Database tables initialized")
except Exception as e:
    print(f"✗ Failed to initialize database: {e}")
    print(f"✗ Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    db_manager = None

@app.route('/')
def home():
    return jsonify({
        'message': 'QR Scanner Backend API with PostgreSQL',
        'version': '2.0.0',
        'database': 'PostgreSQL',
        'endpoints': {
            'scan': '/api/scan',
            'logs': '/api/logs',
            'employees': '/api/employees',
            'statistics': '/api/statistics'
        }
    })

@app.route('/api/scan', methods=['POST'])
def scan_qr():
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'employee_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Employee ID tidak ditemukan dalam request'
            }), 400
        
        employee_id = data['employee_id'].strip().upper()
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        employee = db_manager.get_employee_by_id(employee_id)
        
        if employee:
            db_manager.log_scan_attempt(employee_id, 'SUCCESS', ip_address, user_agent)
            
            return jsonify({
                'success': True,
                'message': f'Akses diterima untuk karyawan {employee_id}',
                'employee_id': employee_id,
                'employee_name': employee['name'],
                'employee_department': employee.get('department', ''),
                'employee_position': employee.get('position', ''),
                'timestamp': datetime.now().isoformat(),
                'status': 'ALLOWED'
            }), 200
        else:
            db_manager.log_scan_attempt(employee_id, 'DENIED', ip_address, user_agent)
            
            return jsonify({
                'success': False,
                'message': f'Akses ditolak. ID karyawan {employee_id} tidak terdaftar atau tidak aktif',
                'employee_id': employee_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'DENIED'
            }), 403
            
    except Exception as e:
        if db_manager:
            db_manager.log_scan_attempt(
                employee_id if 'employee_id' in locals() else 'UNKNOWN', 
                'ERROR', 
                request.remote_addr, 
                request.headers.get('User-Agent', ''),
                str(e)
            )
        
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        employee_id = request.args.get('employee_id')
        status = request.args.get('status')
        
        logs = db_manager.get_scan_logs(limit, offset, employee_id, status)
        
        for log in logs:
            if log['scan_time']:
                log['scan_time'] = log['scan_time'].isoformat()
        
        return jsonify({
            'success': True,
            'logs': logs,
            'total': len(logs),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/employees', methods=['GET'])
def get_employees():
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        employees = db_manager.get_employees(active_only)
        
        for employee in employees:
            if employee['created_at']:
                employee['created_at'] = employee['created_at'].isoformat()
            if employee['updated_at']:
                employee['updated_at'] = employee['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'employees': employees,
            'total': len(employees)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/employees', methods=['POST'])
def add_employee():
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'employee_id' not in data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': 'Employee ID dan name diperlukan'
            }), 400
        
        employee_id = data['employee_id'].strip().upper()
        name = data['name'].strip()
        department = data.get('department', '').strip()
        position = data.get('position', '').strip()
        
        success = db_manager.add_employee(employee_id, name, department, position)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Karyawan {employee_id} berhasil ditambahkan',
                'employee_id': employee_id,
                'name': name
            }), 201
        else:
            return jsonify({
                'success': False,
                'message': 'Employee ID sudah ada'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/employees/<employee_id>', methods=['DELETE'])
def remove_employee(employee_id):
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        employee_id = employee_id.strip().upper()
        
        success = db_manager.update_employee_status(employee_id, False)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Karyawan {employee_id} berhasil dinonaktifkan'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Karyawan {employee_id} tidak ditemukan'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/employees/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        employee_id = employee_id.strip().upper()
        data = request.get_json()
        
        is_active = data.get('is_active', True)
        
        success = db_manager.update_employee_status(employee_id, is_active)
        
        if success:
            status_text = "diaktifkan" if is_active else "dinonaktifkan"
            return jsonify({
                'success': True,
                'message': f'Karyawan {employee_id} berhasil {status_text}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': f'Karyawan {employee_id} tidak ditemukan'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    if not db_manager:
        return jsonify({
            'success': False,
            'message': 'Database connection error'
        }), 500
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        stats = db_manager.get_scan_statistics(start_date, end_date)
        
        for stat in stats:
            if stat['scan_date']:
                stat['scan_date'] = stat['scan_date'].isoformat()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    db_status = 'connected'
    db_info = {}
    total_employees = 0
    
    if db_manager:
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT version() as version')
            result = cursor.fetchone()
            db_version = result['version'] if result else 'Unknown'
            
            cursor.execute('SELECT COUNT(*) as count FROM employees WHERE is_active = TRUE')
            result = cursor.fetchone()
            total_employees = result['count'] if result else 0
            
            cursor.close()
            conn.close()
            
            db_info = {
                'status': 'connected',
                'version': db_version,
                'type': 'PostgreSQL'
            }
        except Exception as e:
            db_status = 'error'
            db_info = {
                'status': 'error',
                'error': str(e),
                'type': 'PostgreSQL'
            }
    else:
        db_status = 'not_connected'
        db_info = {
            'status': 'not_connected',
            'type': 'PostgreSQL'
        }
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'database': db_info,
        'total_active_employees': total_employees
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)