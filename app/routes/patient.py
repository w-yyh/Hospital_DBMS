from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import patient_required

bp = Blueprint('patient', __name__)

@bp.route('/patient/profile/<int:patient_id>', methods=['GET'])
@patient_required
def get_patient_profile(user_id, patient_id):
    if user_id != patient_id:
        return jsonify({'error': '无权访问此信息'}), 403
        
    patient = Database.fetch_one(
        "SELECT * FROM patients WHERE patient_id = %s", (patient_id,)
    )
    return jsonify(patient)

@bp.route('/patient/doctors/<int:patient_id>', methods=['GET'])
@patient_required
def get_patient_doctors(user_id, patient_id):
    if user_id != patient_id:
        return jsonify({'error': '无权访问此信息'}), 403
        
    doctors = Database.fetch_all("""
        SELECT d.* FROM doctors d
        JOIN patient_doctor pd ON d.doctor_id = pd.doctor_id
        WHERE pd.patient_id = %s
    """, (patient_id,))
    return jsonify(doctors) 