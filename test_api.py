import requests
import json
import time

# Base URL untuk API
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_add_employee():
    """Test menambah employee baru"""
    print("Testing add employee...")
    data = {
        "employee_id": "EMP011",
        "name": "Test User",
        "department": "IT",
        "position": "Tester"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/employees", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_get_employees():
    """Test mendapatkan daftar employees"""
    print("Testing get employees...")
    try:
        response = requests.get(f"{BASE_URL}/api/employees")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_scan_valid_employee():
    """Test scan dengan employee ID yang valid (dari database)"""
    print("Testing scan dengan employee ID valid dari database...")
    data = {"employee_id": "EMP001"}
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_scan_new_employee():
    """Test scan dengan employee ID yang baru ditambahkan"""
    print("Testing scan dengan employee ID yang baru ditambahkan...")
    data = {"employee_id": "EMP011"}
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_scan_invalid_employee():
    """Test scan dengan employee ID yang tidak ada di database"""
    print("Testing scan dengan employee ID tidak ada di database...")
    data = {"employee_id": "EMP999"}
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_deactivate_employee():
    """Test menonaktifkan employee"""
    print("Testing deactivate employee...")
    try:
        response = requests.delete(f"{BASE_URL}/api/employees/EMP011")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_scan_deactivated_employee():
    """Test scan dengan employee yang sudah dinonaktifkan"""
    print("Testing scan dengan employee yang sudah dinonaktifkan...")
    data = {"employee_id": "EMP011"}
    try:
        response = requests.post(f"{BASE_URL}/api/scan", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_reactivate_employee():
    """Test mengaktifkan kembali employee"""
    print("Testing reactivate employee...")
    data = {"is_active": True}
    try:
        response = requests.put(f"{BASE_URL}/api/employees/EMP011", json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_get_logs():
    """Test mendapatkan logs"""
    print("Testing get logs...")
    try:
        response = requests.get(f"{BASE_URL}/api/logs?limit=10")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_get_statistics():
    """Test mendapatkan statistik"""
    print("Testing get statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/statistics")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 50)

if __name__ == "__main__":
    print("Starting API Tests - Database Only Mode...")
    print("=" * 50)
    
    # Test sequence
    test_health_check()
    test_get_employees()
    test_add_employee()
    test_scan_valid_employee()
    test_scan_new_employee()
    test_scan_invalid_employee()
    test_deactivate_employee()
    test_scan_deactivated_employee()
    test_reactivate_employee()
    test_get_logs()
    test_get_statistics()
    
    print("All tests completed!")
    print("\nCatatan:")
    print("- Semua validasi employee sekarang hanya dari database")
    print("- Tidak ada lagi ALLOWED_EMPLOYEE_IDS hardcoded")
    print("- Employee yang tidak aktif tidak bisa scan")