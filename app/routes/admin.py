from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import admin_required

bp = Blueprint('admin', __name__)

@bp.route('/admin/doctors', methods=['GET'])
@admin_required
def get_all_doctors(admin_id):
    doctors = Database.fetch_all("SELECT * FROM doctors")
    return jsonify(doctors)

@bp.route('/admin/doctor', methods=['POST'])
@admin_required
def add_doctor(admin_id):
    data = request.get_json()
    Database.execute_query("""
        INSERT INTO doctors (doctor_id, name, dob, contact_number, specialization, 
                           department_id, email) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data['doctor_id'], data['name'], data['dob'], data['contact_number'],
          data['specialization'], data['department_id'], data['email']))
    return jsonify({'message': 'Doctor added successfully'})

@bp.route('/admin/test-db', methods=['GET'])
def test_database():
    try:
        # 测试查询每个表
        departments = Database.fetch_all("SELECT * FROM departments")
        doctors = Database.fetch_all("SELECT * FROM doctors")
        nurses = Database.fetch_all("SELECT * FROM nurses")
        
        return jsonify({
            'status': 'success',
            'data': {
                'departments_count': len(departments),
                'doctors_count': len(doctors),
                'nurses_count': len(nurses)
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 