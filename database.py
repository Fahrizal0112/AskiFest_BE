import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
from config import Config

class DatabaseManager:
    
    def __init__(self, database_url=None):
        self.database_url = database_url or Config.DATABASE_URL
        self.init_database()
    
    def get_connection(self):
        try:
            conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            return conn
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_logs (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) NOT NULL,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) NOT NULL CHECK(status IN ('SUCCESS', 'DENIED', 'ERROR')),
                    ip_address INET,
                    user_agent TEXT,
                    additional_info TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    department VARCHAR(100),
                    position VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_settings (
                    id SERIAL PRIMARY KEY,
                    setting_key VARCHAR(100) UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_logs_employee_id ON scan_logs(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_logs_scan_time ON scan_logs(scan_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_employee_id ON employees(employee_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_employees_is_active ON employees(is_active)')
            
            cursor.execute('''
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            ''')
            
            cursor.execute('''
                DROP TRIGGER IF EXISTS update_employees_updated_at ON employees
            ''')
            
            cursor.execute('''
                CREATE TRIGGER update_employees_updated_at
                    BEFORE UPDATE ON employees
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()
            ''')
            
            cursor.execute('SELECT COUNT(*) FROM employees')
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_employees = [
                    ('EMP001', 'John Doe', 'IT', 'Software Developer'),
                    ('EMP002', 'Jane Smith', 'HR', 'HR Manager'),
                    ('EMP003', 'Bob Johnson', 'Finance', 'Accountant'),
                    ('EMP004', 'Alice Brown', 'IT', 'System Administrator'),
                    ('EMP005', 'Charlie Wilson', 'Marketing', 'Marketing Specialist')
                ]
                
                cursor.executemany('''
                    INSERT INTO employees (employee_id, name, department, position)
                    VALUES (%s, %s, %s, %s)
                ''', sample_employees)
                
                print("Sample employees data inserted")
            
            conn.commit()
            print("Database initialized successfully")
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def log_scan_attempt(self, employee_id, status, ip_address=None, user_agent=None, additional_info=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO scan_logs (employee_id, status, ip_address, user_agent, additional_info)
                VALUES (%s, %s, %s, %s, %s)
            ''', (employee_id, status, ip_address, user_agent, additional_info))
            
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error logging scan attempt: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_scan_logs(self, limit=50, offset=0, employee_id=None, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT sl.*, e.name as employee_name, e.department 
                FROM scan_logs sl
                LEFT JOIN employees e ON sl.employee_id = e.employee_id
                WHERE 1=1
            '''
            params = []
            
            if employee_id:
                query += ' AND sl.employee_id = %s'
                params.append(employee_id)
            
            if status:
                query += ' AND sl.status = %s'
                params.append(status)
            
            query += ' ORDER BY sl.scan_time DESC LIMIT %s OFFSET %s'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            logs = [dict(row) for row in cursor.fetchall()]
            
            return logs
            
        except psycopg2.Error as e:
            print(f"Error getting scan logs: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def add_employee(self, employee_id, name, department=None, position=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees (employee_id, name, department, position)
                VALUES (%s, %s, %s, %s)
            ''', (employee_id, name, department, position))
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error adding employee: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_employees(self, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = 'SELECT * FROM employees'
            if active_only:
                query += ' WHERE is_active = TRUE'
            query += ' ORDER BY name'
            
            cursor.execute(query)
            employees = [dict(row) for row in cursor.fetchall()]
            
            return employees
            
        except psycopg2.Error as e:
            print(f"Error getting employees: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_employee_status(self, employee_id, is_active):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE employees 
                SET is_active = %s
                WHERE employee_id = %s
            ''', (is_active, employee_id))
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            return affected_rows > 0
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error updating employee status: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_employee_by_id(self, employee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM employees 
                WHERE employee_id = %s AND is_active = TRUE
            ''', (employee_id,))
            
            employee = cursor.fetchone()
            return dict(employee) if employee else None
            
        except psycopg2.Error as e:
            print(f"Error getting employee by ID: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_employee_info(self, employee_id, name=None, department=None, position=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if name:
                updates.append('name = %s')
                params.append(name)
            
            if department is not None:
                updates.append('department = %s')
                params.append(department)
            
            if position is not None:
                updates.append('position = %s')
                params.append(position)
            
            if not updates:
                return False
            
            query = f'''
                UPDATE employees 
                SET {', '.join(updates)}
                WHERE employee_id = %s
            '''
            params.append(employee_id)
            
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            conn.commit()
            
            return affected_rows > 0
            
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Error updating employee info: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_scan_statistics(self, start_date=None, end_date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    status,
                    COUNT(*) as count,
                    DATE(scan_time) as scan_date
                FROM scan_logs 
                WHERE 1=1
            '''
            params = []
            
            if start_date:
                query += ' AND scan_time >= %s'
                params.append(start_date)
            
            if end_date:
                query += ' AND scan_time <= %s'
                params.append(end_date)
            
            query += ' GROUP BY status, DATE(scan_time) ORDER BY scan_date DESC'
            
            cursor.execute(query, params)
            stats = [dict(row) for row in cursor.fetchall()]
            
            return stats
            
        except psycopg2.Error as e:
            print(f"Error getting scan statistics: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_employee_scan_summary(self, employee_id=None, days=30):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT 
                    e.employee_id,
                    e.name,
                    e.department,
                    COUNT(sl.id) as total_scans,
                    COUNT(CASE WHEN sl.status = 'SUCCESS' THEN 1 END) as successful_scans,
                    COUNT(CASE WHEN sl.status = 'DENIED' THEN 1 END) as denied_scans,
                    MAX(sl.scan_time) as last_scan
                FROM employees e
                LEFT JOIN scan_logs sl ON e.employee_id = sl.employee_id 
                    AND sl.scan_time >= CURRENT_DATE - INTERVAL '%s days'
                WHERE e.is_active = TRUE
            '''
            params = [days]
            
            if employee_id:
                query += ' AND e.employee_id = %s'
                params.append(employee_id)
            
            query += ' GROUP BY e.employee_id, e.name, e.department ORDER BY total_scans DESC'
            
            cursor.execute(query, params)
            summary = [dict(row) for row in cursor.fetchall()]
            
            return summary
            
        except psycopg2.Error as e:
            print(f"Error getting employee scan summary: {e}")
            raise
        finally:
            cursor.close()
            conn.close()