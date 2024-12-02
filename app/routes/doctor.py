from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import doctor_required

bp = Blueprint('doctor', __name__)

@bp.route('/doctor/patients', methods=['GET'])
@doctor_required
def get_doctor_patients(doctor_id):
    patients = Database.fetch_all("""
        SELECT p.* FROM patients p
        JOIN patient_doctor pd ON p.patient_id = pd.patient_id
        WHERE pd.doctor_id = %s
    """, (doctor_id,))
    return jsonify(patients)

@bp.route('/doctor/update-diagnosis', methods=['POST'])
@doctor_required
def update_diagnosis(doctor_id):
    data = request.get_json()
    Database.execute_query("""
        UPDATE patient_doctor 
        SET diagnosis = %s 
        WHERE patient_id = %s AND doctor_id = %s
    """, (data['diagnosis'], data['patient_id'], doctor_id))
    return jsonify({'message': 'Diagnosis updated successfully'}) 