from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import patient_required
from datetime import datetime

bp = Blueprint('patient', __name__)

@bp.route('/patient/profile/<int:patient_id>', methods=['GET'])
@patient_required
def get_patient_profile(user_id, patient_id):
    try:
        # 获取患者ID
        patient = Database.fetch_one("""
            SELECT * FROM patients 
            WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not patient:
            return jsonify({'error': '患者信息不存在'}), 404
            
        return jsonify(patient), 200
        
    except Exception as e:
        print(f"Error getting patient profile: {str(e)}")
        return jsonify({'error': '获取患者信息失败'}), 500

@bp.route('/patient', methods=['POST'])
@patient_required
def create_patient(user_id):
    data = request.get_json()
    required_fields = ['name', 'birth_date', 'contact', 'address', 'gender']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 创建患者记录
        patient_id = Database.execute("""
            INSERT INTO patients (
                user_id, name, birth_date, gender, 
                contact, address, medical_history
            ) VALUES (
                :user_id, :name, :birth_date, :gender,
                :contact, :address, :medical_history
            ) RETURNING id
        """, {
            'user_id': user_id,
            'name': data['name'],
            'birth_date': data['birth_date'],
            'gender': data['gender'],
            'contact': data['contact'],
            'address': data['address'],
            'medical_history': data.get('medical_history', '')
        })
        
        return jsonify({
            'message': '患者记录创建成功',
            'patient_id': patient_id
        }), 201
        
    except Exception as e:
        print(f"Error creating patient: {str(e)}")
        return jsonify({'error': '创建患者记录失败'}), 500

@bp.route('/patient/<int:patient_id>', methods=['PUT'])
@patient_required
def update_patient(user_id, patient_id):
    try:
        # 获取患者信息
        patient = Database.fetch_one("""
            SELECT * FROM patients 
            WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not patient:
            return jsonify({'error': '患者信息不存在'}), 404
            
        data = request.get_json()
        allowed_fields = ['name', 'birth_date', 'contact', 'address', 'gender']
        update_data = {}
        update_fields = []
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = :{field}")
                update_data[field] = data[field]
        
        if not update_fields:
            return jsonify({'error': '没有提供要更新的字段'}), 400
            
        update_data['user_id'] = user_id
        
        Database.execute(f"""
            UPDATE patients 
            SET {', '.join(update_fields)}
            WHERE user_id = :user_id
        """, update_data)
        
        return jsonify({'message': '患者信息更新成功'})
    except Exception as e:
        print(f"Error updating patient: {str(e)}")
        return jsonify({'error': '更新患者信息失败'}), 500

@bp.route('/patient/doctors/<int:patient_id>', methods=['GET'])
@patient_required
def get_patient_doctors(user_id, patient_id):
    try:
        # 获取患者信息
        patient = Database.fetch_one("""
            SELECT * FROM patients 
            WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not patient:
            return jsonify({'error': '患者信息不存在'}), 404
            
        doctors = Database.fetch_all("""
            SELECT 
                d.id,
                d.name,
                d.specialization,
                d.contact,
                pd.start_date as relationship_start
            FROM doctors d
            JOIN patient_doctor pd ON d.id = pd.doctor_id
            WHERE pd.patient_id = :patient_id
            ORDER BY pd.start_date DESC
        """, {'patient_id': patient_id})
        
        return jsonify(doctors or []), 200
    except Exception as e:
        print(f"Error getting patient doctors: {str(e)}")
        return jsonify({'error': '获取医生列表失败'}), 500 