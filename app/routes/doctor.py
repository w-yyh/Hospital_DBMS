from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import doctor_required
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import string
import random

bp = Blueprint('doctor', __name__)
# 已实现功能：
# 1. 获取医生个人信息
# 2. 创建医生个人信息
# 3. 更新医生个人信息
# 4. 删除医生个人信息
# 5. 获取医生患者信息
# 6. 更新医生诊断信息
# 7. 治疗记录管理


@bp.route('/doctor/profile/<int:doctor_id>', methods=['GET'])
@doctor_required
def get_doctor_profile(user_id, doctor_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT user_id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
            
        # 获取医生信息
        doctor_info = Database.fetch_one("""
            SELECT d.*, dp.name as department_name 
            FROM doctors d
            LEFT JOIN departments dp ON d.department_id = dp.id
            WHERE d.user_id = :doctor_id
        """, {'doctor_id': doctor_id})
        
        if not doctor_info:
            return jsonify({'error': '医生不存在'}), 404
            
        return jsonify(doctor_info), 200
        
    except Exception as e:
        print(f"Error getting doctor profile: {str(e)}")
        return jsonify({'error': '获取医生信息失败'}), 500

@bp.route('/doctor', methods=['POST'])
@doctor_required
def create_doctor(user_id):
    data = request.get_json()
    required_fields = ['name', 'birth_date', 'contact', 'email', 'department_id', 'specialization']
    
    # 验证必填字段
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
    
    try:
        # 验证科室是否存在
        department = Database.fetch_one("""
            SELECT id FROM departments 
            WHERE id = :department_id
        """, {'department_id': data['department_id']})
        
        if not department:
            return jsonify({'error': '指定的科室不存在'}), 400
        
        # 创建医生记录
        doctor_id = Database.execute("""
            INSERT INTO doctors (
                user_id,
                name, 
                birth_date, 
                contact, 
                email, 
                department_id, 
                specialization
            ) VALUES (
                :user_id,
                :name, 
                :birth_date, 
                :contact, 
                :email, 
                :department_id, 
                :specialization
            ) RETURNING id
        """, {
            'user_id': user_id,
            'name': data['name'],
            'birth_date': data['birth_date'],
            'contact': data['contact'],
            'email': data['email'],
            'department_id': data['department_id'],
            'specialization': data['specialization']
        })
        
        return jsonify({
            'message': '医生创建成功',
            'doctor_id': doctor_id
        }), 201
        
    except Exception as e:
        print(f"Error creating doctor: {str(e)}")
        return jsonify({'error': '创建医生失败'}), 500

@bp.route('/doctor/<int:doctor_id>', methods=['PUT'])
@doctor_required
def update_doctor(user_id, doctor_id):
    if user_id != doctor_id:
        return jsonify({'error': '无权修改此医生信息'}), 403
        
    data = request.get_json()
    allowed_fields = ['name', 'birth_date', 'contact', 'email', 'department_id', 'specialization']
    update_data = {}
    update_fields = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            update_data[field] = data[field]
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
    
    try:
        # 如果更新科室，验证科室是否存在
        if 'department_id' in update_data:
            department = Database.fetch_one("""
                SELECT id FROM departments WHERE id = :department_id
            """, {'department_id': update_data['department_id']})
            
            if not department:
                return jsonify({'error': '指定的科室不存在'}), 400
        
        update_data['user_id'] = user_id
        Database.execute(f"""
            UPDATE doctors 
            SET {', '.join(update_fields)}
            WHERE user_id = :user_id
        """, update_data)
        
        return jsonify({'message': '医生信息更新成功'})
    except Exception as e:
        print(f"Error updating doctor: {str(e)}")
        return jsonify({'error': '更新医生信息失败'}), 500

@bp.route('/doctor/<int:doctor_id>', methods=['DELETE'])
@doctor_required
def delete_doctor(user_id, doctor_id):
    if user_id != doctor_id:
        return jsonify({'error': '无权删除此医生信息'}), 403
    
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 检查是否存在相关的预约
        related_records = Database.fetch_one("""
            SELECT COUNT(*) as count 
            FROM appointments 
            WHERE doctor_id = :doctor_id AND appointment_time > CURRENT_TIMESTAMP
        """, {'doctor_id': doctor['id']})
        
        if related_records['count'] > 0:
            return jsonify({'error': '该医生还有未完成的预约，无法删除'}), 400
            
        # 软删除医生记录
        Database.execute("""
            UPDATE doctors 
            SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP
            WHERE id = :doctor_id
        """, {'doctor_id': doctor['id']})
        
        return jsonify({'message': '医生记录已删除'})
    except Exception as e:
        print(f"Error deleting doctor: {str(e)}")
        return jsonify({'error': '删除医生失败'}), 500

@bp.route('/doctor/update-diagnosis', methods=['POST'])
@doctor_required
def update_diagnosis(user_id):
    data = request.get_json()
    try:
        Database.execute_query("""
            UPDATE patient_doctor 
            SET diagnosis = :diagnosis 
            WHERE patient_id = :patient_id AND doctor_id = :doctor_id
        """, {
            'diagnosis': data['diagnosis'],
            'patient_id': data['patient_id'],
            'doctor_id': user_id
        })
        return jsonify({'message': '诊断信息更新成功'})
    except Exception as e:
        print(f"Error updating diagnosis: {str(e)}")
        return jsonify({'error': '更新诊断信息失败'}), 500

# 治疗记录管理相关路由
@bp.route('/doctor/treatment', methods=['POST'])
@doctor_required
def create_treatment(user_id):
    data = request.get_json()
    required_fields = ['patient_id', 'diagnosis', 'treatment_plan', 'medications']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证患者是否存在且与该医生关联
        patient = Database.fetch_one("""
            SELECT p.id 
            FROM patients p
            JOIN patient_doctor pd ON p.id = pd.patient_id
            WHERE p.id = :patient_id AND pd.doctor_id = :doctor_id
        """, {
            'patient_id': data['patient_id'],
            'doctor_id': doctor['id']
        })
        
        if not patient:
            return jsonify({'error': '无权为此患者创建治疗记录'}), 403
            
        treatment_id = Database.execute("""
            INSERT INTO treatments (
                patient_id, doctor_id, diagnosis, treatment_plan,
                medications, treatment_date, notes
            ) VALUES (
                :patient_id, :doctor_id, :diagnosis, :treatment_plan,
                :medications, CURRENT_DATE, :notes
            ) RETURNING id
        """, {
            'patient_id': data['patient_id'],
            'doctor_id': doctor['id'],
            'diagnosis': data['diagnosis'],
            'treatment_plan': data['treatment_plan'],
            'medications': data['medications'],
            'notes': data.get('notes', '')
        })
        
        return jsonify({
            'message': '治疗记录创建成功',
            'treatment_id': treatment_id
        }), 201
    except Exception as e:
        print(f"Error creating treatment: {str(e)}")
        return jsonify({'error': '创建治疗记录失败'}), 500

@bp.route('/doctor/treatment/<int:treatment_id>', methods=['GET'])
@doctor_required
def get_treatment(user_id, treatment_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        treatment = Database.fetch_one("""
            SELECT t.*, p.name as patient_name
            FROM treatments t
            JOIN patients p ON t.patient_id = p.id
            WHERE t.id = :treatment_id AND t.doctor_id = :doctor_id
        """, {
            'treatment_id': treatment_id,
            'doctor_id': doctor['id']
        })
        
        if not treatment:
            return jsonify({'error': '治疗记录不存在或无权访问'}), 404
            
        return jsonify(treatment)
    except Exception as e:
        print(f"Error getting treatment: {str(e)}")
        return jsonify({'error': '获取治疗记录失败'}), 500

@bp.route('/doctor/patient/<int:patient_id>/treatments', methods=['GET'])
@doctor_required
def get_patient_treatments(user_id, patient_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证患者是否与该医生关联
        patient = Database.fetch_one("""
            SELECT p.id 
            FROM patients p
            JOIN patient_doctor pd ON p.id = pd.patient_id
            WHERE p.id = :patient_id AND pd.doctor_id = :doctor_id
        """, {
            'patient_id': patient_id,
            'doctor_id': doctor['id']
        })
        
        if not patient:
            return jsonify({'error': '无权查看此患者的治疗记录'}), 403
            
        treatments = Database.fetch_all("""
            SELECT t.*, p.name as patient_name
            FROM treatments t
            JOIN patients p ON t.patient_id = p.id
            WHERE t.patient_id = :patient_id AND t.doctor_id = :doctor_id
            ORDER BY t.treatment_date DESC
        """, {
            'patient_id': patient_id,
            'doctor_id': doctor['id']
        })
        
        return jsonify(treatments or []), 200
    except Exception as e:
        print(f"Error getting patient treatments: {str(e)}")
        return jsonify({'error': '获取患者治疗记录失败'}), 500

@bp.route('/doctor/treatment/<int:treatment_id>', methods=['PUT'])
@doctor_required
def update_treatment(user_id, treatment_id):
    data = request.get_json()
    allowed_fields = ['diagnosis', 'treatment_plan', 'medications', 'notes']
    update_data = {}
    update_fields = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            update_data[field] = data[field]
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
    
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证治疗记录是否存在且属于该医生
        treatment = Database.fetch_one("""
            SELECT id FROM treatments
            WHERE id = :treatment_id AND doctor_id = :doctor_id
        """, {
            'treatment_id': treatment_id,
            'doctor_id': doctor['id']
        })
        
        if not treatment:
            return jsonify({'error': '治疗记录不存在或无权修改'}), 404
            
        update_data.update({
            'treatment_id': treatment_id,
            'doctor_id': doctor['id']
        })
        
        Database.execute(f"""
            UPDATE treatments 
            SET {', '.join(update_fields)}
            WHERE id = :treatment_id AND doctor_id = :doctor_id
        """, update_data)
        
        return jsonify({'message': '治疗记录更新成功'})
    except Exception as e:
        print(f"Error updating treatment: {str(e)}")
        return jsonify({'error': '更新治疗记录失败'}), 500

@bp.route('/doctor/treatment/<int:treatment_id>', methods=['DELETE'])
@doctor_required
def delete_treatment(user_id, treatment_id):
    try:
        # 验治疗记录是否存在且属于该医生
        treatment = Database.fetch_one("""
            SELECT treatment_id, created_at 
            FROM treatments
            WHERE treatment_id = %s AND doctor_id = %s
        """, (treatment_id, user_id))
        
        if not treatment:
            return jsonify({'error': '治疗记录不存在或无权删除'}), 404
            
        # 检查记录创建时间，如果超过24小时则不允许删除
        time_diff = datetime.now() - treatment['created_at']
        if time_diff.days >= 1:
            return jsonify({'error': '治疗记录创建超过24小时，无法删除'}), 400
            
        # 软删除治疗记录
        Database.execute("""
            UPDATE treatments 
            SET is_deleted = TRUE, deleted_at = NOW()
            WHERE treatment_id = %s AND doctor_id = %s
        """, (treatment_id, user_id))
        
        return jsonify({'message': '治疗记录已删除'})
    except Exception as e:
        return jsonify({'error': f'删除治疗记录失败: {str(e)}'}), 500

# 医生-患者关系管理相关路由
@bp.route('/doctor/patient-relation', methods=['POST'])
@doctor_required
def create_patient_relation(user_id):
    data = request.get_json()
    required_fields = ['patient_id', 'visit_date']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证患者是否存在
        patient = Database.fetch_one("""
            SELECT id FROM patients WHERE id = :patient_id
        """, {'patient_id': data['patient_id']})
        
        if not patient:
            return jsonify({'error': '患者不存在'}), 404
            
        # 创建关联记录
        relation_id = Database.execute("""
            INSERT INTO patient_doctor (
                patient_id, doctor_id, start_date, notes
            ) VALUES (
                :patient_id, :doctor_id, :start_date, :notes
            ) RETURNING id
        """, {
            'patient_id': data['patient_id'],
            'doctor_id': doctor['id'],
            'start_date': data['visit_date'],
            'notes': data.get('initial_diagnosis', '')
        })
        
        return jsonify({
            'message': '医患关系创建成功',
            'relation_id': relation_id
        }), 201
        
    except Exception as e:
        print(f"Error creating patient relation: {str(e)}")
        return jsonify({'error': '创建医患关系失败'}), 500

@bp.route('/doctor/patient-relations', methods=['GET'])
@doctor_required
def get_patient_relations(user_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 获取所有关联的患者信息
        relations = Database.fetch_all("""
            SELECT 
                pd.*, 
                p.name as patient_name, 
                p.contact as patient_contact,
                p.gender as patient_gender,
                p.birth_date as patient_birth_date
            FROM patient_doctor pd
            JOIN patients p ON pd.patient_id = p.id
            WHERE pd.doctor_id = :doctor_id
            ORDER BY pd.start_date DESC
        """, {'doctor_id': doctor['id']})
        
        return jsonify(relations or [])
    except Exception as e:
        print(f"Error getting patient relations: {str(e)}")
        return jsonify({'error': '获取医患关系列表失败'}), 500

@bp.route('/doctor/patient-relation/<int:relation_id>', methods=['GET'])
@doctor_required
def get_patient_relation(user_id, relation_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 获取特定关联记录的详细信息
        relation = Database.fetch_one("""
            SELECT 
                pd.*, 
                p.name as patient_name, 
                p.contact as patient_contact,
                p.gender as patient_gender,
                p.birth_date as patient_birth_date,
                array_agg(t.id) as treatment_ids,
                array_agg(t.diagnosis) as diagnoses,
                array_agg(t.treatment_date) as treatment_dates
            FROM patient_doctor pd
            JOIN patients p ON pd.patient_id = p.id
            LEFT JOIN treatments t ON pd.patient_id = t.patient_id 
                AND pd.doctor_id = t.doctor_id
            WHERE pd.id = :relation_id AND pd.doctor_id = :doctor_id
            GROUP BY pd.id, p.id
        """, {
            'relation_id': relation_id,
            'doctor_id': doctor['id']
        })
        
        if not relation:
            return jsonify({'error': '医患关系记录不存在或无权访问'}), 404
            
        return jsonify(relation)
    except Exception as e:
        print(f"Error getting patient relation: {str(e)}")
        return jsonify({'error': '获取医患关系详情失败'}), 500

@bp.route('/doctor/patient-relation/<int:relation_id>', methods=['PUT'])
@doctor_required
def update_patient_relation(user_id, relation_id):
    data = request.get_json()
    allowed_fields = ['visit_date', 'diagnosis', 'status', 'notes']
    update_data = {}
    update_fields = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = :{field}")
            update_data[field] = data[field]
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
    
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证关联记录是否存在且属于该医生
        relation = Database.fetch_one("""
            SELECT id FROM patient_doctor
            WHERE id = :relation_id AND doctor_id = :doctor_id
        """, {
            'relation_id': relation_id,
            'doctor_id': doctor['id']
        })
        
        if not relation:
            return jsonify({'error': '医患关系记录不存在或无权修改'}), 404
            
        update_data.update({
            'relation_id': relation_id,
            'doctor_id': doctor['id']
        })
        
        Database.execute(f"""
            UPDATE patient_doctor 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :relation_id AND doctor_id = :doctor_id
        """, update_data)
        
        return jsonify({'message': '医患关系更新成功'})
    except Exception as e:
        print(f"Error updating patient relation: {str(e)}")
        return jsonify({'error': '更新医患关系失败'}), 500

@bp.route('/doctor/patient-relation/<int:relation_id>', methods=['DELETE'])
@doctor_required
def delete_patient_relation(user_id, relation_id):
    try:
        # 验证关联记录是否存在且属于该医生
        relation = Database.fetch_one("""
            SELECT relation_id, created_at 
            FROM patient_doctor
            WHERE relation_id = %s AND doctor_id = %s
        """, (relation_id, user_id))
        
        if not relation:
            return jsonify({'error': '医患关系记录不存在或无权删除'}), 404
            
        # 检查是否有相关的治疗记录
        treatments = Database.fetch_one("""
            SELECT COUNT(*) as count 
            FROM treatments
            WHERE patient_id = (
                SELECT patient_id 
                FROM patient_doctor 
                WHERE relation_id = %s
            ) AND doctor_id = %s
        """, (relation_id, user_id))
        
        if treatments['count'] > 0:
            return jsonify({
                'error': '存在相关的治疗记录，无法删除医患关系',
                'treatment_count': treatments['count']
            }), 400
            
        # 软删除关联记录
        Database.execute("""
            UPDATE patient_doctor 
            SET is_deleted = TRUE, deleted_at = NOW()
            WHERE relation_id = %s AND doctor_id = %s
        """, (relation_id, user_id))
        
        return jsonify({'message': '医患关系已删除'})
    except Exception as e:
        return jsonify({'error': f'删除医患关系失败: {str(e)}'}), 500

# 患者入住记录管理相关路由
@bp.route('/doctor/admission', methods=['POST'])
@doctor_required
def create_admission(user_id):
    data = request.get_json()
    required_fields = ['patient_id', 'ward_id', 'admission_date', 'expected_discharge_date']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证患者是否存在且与该医生关联
        patient = Database.fetch_one("""
            SELECT p.id 
            FROM patients p
            JOIN patient_doctor pd ON p.id = pd.patient_id
            WHERE p.id = :patient_id AND pd.doctor_id = :doctor_id
        """, {
            'patient_id': data['patient_id'],
            'doctor_id': doctor['id']
        })
        
        if not patient:
            return jsonify({'error': '无权为此患者创建入住记录'}), 403
            
        # 验证病房是否存在且有空床位
        ward = Database.fetch_one("""
            SELECT w.*, 
                   COUNT(a.id) as current_patients
            FROM wards w
            LEFT JOIN admissions a ON w.id = a.ward_id 
                AND a.discharge_date IS NULL
                AND a.is_deleted = FALSE
            WHERE w.id = :ward_id
            GROUP BY w.id
        """, {'ward_id': data['ward_id']})
        
        if not ward:
            return jsonify({'error': '病房不存在'}), 404
            
        if ward['current_patients'] >= ward['bed_count']:
            return jsonify({'error': '该病房已无空床位'}), 400
            
        # 检查患者是否已有未结束的住院记录
        existing_admission = Database.fetch_one("""
            SELECT id FROM admissions 
            WHERE patient_id = :patient_id 
            AND discharge_date IS NULL 
            AND is_deleted = FALSE
        """, {'patient_id': data['patient_id']})
        
        if existing_admission:
            return jsonify({'error': '该患者已有未结束的住院记录'}), 400
            
        # 创建入住记录
        admission_id = Database.execute("""
            INSERT INTO admissions (
                patient_id, doctor_id, ward_id,
                admission_date, expected_discharge_date,
                notes
            ) VALUES (
                :patient_id, :doctor_id, :ward_id,
                :admission_date, :expected_discharge_date,
                :notes
            ) RETURNING id
        """, {
            'patient_id': data['patient_id'],
            'doctor_id': doctor['id'],
            'ward_id': data['ward_id'],
            'admission_date': data['admission_date'],
            'expected_discharge_date': data['expected_discharge_date'],
            'notes': data.get('notes', '')
        })
        
        return jsonify({
            'message': '入住记录创建成功',
            'admission_id': admission_id
        }), 201
        
    except Exception as e:
        print(f"Error creating admission: {str(e)}")
        return jsonify({'error': '创建入住记录失败'}), 500

@bp.route('/doctor/admission/<int:admission_id>', methods=['DELETE'])
@doctor_required
def delete_admission(user_id, admission_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证入住记录是否存在且属于该医生
        admission = Database.fetch_one("""
            SELECT id, created_at 
            FROM admissions
            WHERE id = :admission_id AND doctor_id = :doctor_id
        """, {
            'admission_id': admission_id,
            'doctor_id': doctor['id']
        })
        
        if not admission:
            return jsonify({'error': '入住记录不存在或无权删除'}), 404
            
        # 检查记录创建时间，如果超过24小时则不允许删除
        time_diff = datetime.now() - admission['created_at']
        if time_diff.days >= 1:
            return jsonify({'error': '入住记录创建超过24小时，无法删除'}), 400
            
        # 软删除入住记录
        Database.execute("""
            UPDATE admissions 
            SET is_deleted = TRUE, deleted_at = CURRENT_TIMESTAMP
            WHERE id = :admission_id AND doctor_id = :doctor_id
        """, {
            'admission_id': admission_id,
            'doctor_id': doctor['id']
        })
        
        return jsonify({'message': '入住记录已删除'})
    except Exception as e:
        print(f"Error deleting admission: {str(e)}")
        return jsonify({'error': '删除入住记录失败'}), 500



@bp.route('/doctor/patient', methods=['POST'])
@doctor_required
def add_patient_doctor_relationship(user_id):
    """
    增添医生与新患者的关联记录，同时在 patients 表中创建新的患者记录，
    并在 users 表中生成对应的用户名和密码。
    """
    try:
        data = request.get_json()
        # 定义需要的患者信息字段
        required_fields = ['name', 'birth_date', 'gender']

        # 检查请求体是否为空
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        # 检查必填字段是否齐全
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f"缺少必填字段: {', '.join(missing_fields)}"}), 400

        name = data['name']
        birth_date = data['birth_date']
        gender = data['gender']
        contact = data.get('contact', '')
        address = data.get('address', '')
        medical_history = data.get('medical_history', '')
        notes = data.get('notes', '')

        # 生成随机用户名和密码
        username = generate_random_username()
        password = generate_random_password()
        password_hash = generate_password_hash(password)

        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})

        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404

        doctor_id = doctor['id']

        # 开始数据库操作
        try:
            # 插入新用户到 users 表
            insert_user_query = """
                INSERT INTO users (username, password_hash, role)
                VALUES (:username, :password_hash, :role)
                RETURNING id
            """
            user_params = {
                'username': username,
                'password_hash': password_hash,
                'role': 'patient'
            }
            user_id_new = Database.execute(insert_user_query, user_params)

            if not user_id_new:
                return jsonify({'error': '创建用户失败'}), 500

            # 插入新患者到 patients 表
            insert_patient_query = """
                INSERT INTO patients (user_id, name, birth_date, gender, contact, address, medical_history)
                VALUES (:user_id, :name, :birth_date, :gender, :contact, :address, :medical_history)
                RETURNING id
            """
            patient_params = {
                'user_id': user_id_new,
                'name': name,
                'birth_date': birth_date,
                'gender': gender,
                'contact': contact,
                'address': address,
                'medical_history': medical_history
            }
            patient_id_new = Database.execute(insert_patient_query, patient_params)

            if not patient_id_new:
                return jsonify({'error': '创建患者失败'}), 500

            # 可选：在 patient_doctor 表中关联医生与新患者
            insert_relationship_query = """
                INSERT INTO patient_doctor (doctor_id, patient_id, start_date, notes)
                VALUES (:doctor_id, :patient_id, :start_date, :notes)
                RETURNING id
            """
            relationship_params = {
                'doctor_id': doctor_id,
                'patient_id': patient_id_new,
                'start_date': datetime.utcnow().date(),
                'notes': notes
            }
            relationship_id = Database.execute(insert_relationship_query, relationship_params)

            if not relationship_id:
                return jsonify({'error': '关联医生与患者失败'}), 500

            # 返回新患者的相关信息，包括用户名和初始密码
            return jsonify({
                'message': '新患者已成功添加并关联到医生',
                'patient_id': patient_id_new,
                'username': username,
                'password': password,  # 注意：在生产环境中，建议通过安全渠道传输密码
                'relationship_id': relationship_id
            }), 201

        except Exception as e:
            print(f"Error adding new patient and relationship: {str(e)}")
            return jsonify({'error': '服务器内部错误'}), 500

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

def generate_random_username(length=8):
    """生成一个指定长度的随机用户名，包含字母和数字"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_random_password(length=12):
    """生成一个指定长度的随机密码，包含字母、数字和符号"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@bp.route('/doctor/patient/<int:patient_id>/doctors', methods=['GET'])
@doctor_required
def get_patient_doctors(user_id, patient_id):
    """获取患者的主治医生列表"""
    try:
        # 验证患者是否存在
        patient = Database.fetch_one("""
            SELECT id FROM patients WHERE id = :patient_id
        """, {'patient_id': patient_id})
        
        if not patient:
            return jsonify({'error': '患者不存在'}), 404
            
        # 获取医生列表
        doctors = Database.fetch_all("""
            SELECT 
                d.id,
                d.name,
                d.specialization,
                d.contact,
                pd.start_date as relationship_start,
                pd.notes
            FROM doctors d
            JOIN patient_doctor pd ON d.id = pd.doctor_id
            WHERE pd.patient_id = :patient_id
            ORDER BY pd.start_date DESC
        """, {'patient_id': patient_id})
        
        return jsonify(doctors or []), 200
        
    except Exception as e:
        print(f"Error getting patient's doctors: {str(e)}")
        return jsonify({'error': '获取医生列表失败'}), 500
    
    
@bp.route('/doctor/admission/<int:admission_id>', methods=['PUT'])
@doctor_required
def update_admission(user_id, admission_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证入院记录是否存在且属于该医生
        admission = Database.fetch_one("""
            SELECT id FROM admissions 
            WHERE id = :admission_id 
            AND doctor_id = :doctor_id
            AND is_deleted = FALSE
        """, {
            'admission_id': admission_id,
            'doctor_id': doctor['id']
        })
        
        if not admission:
            return jsonify({'error': '入院记录不存在或无权修改'}), 404
            
        data = request.get_json()
        allowed_fields = ['discharge_date', 'notes']
        update_data = {}
        update_fields = []
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = :{field}")
                update_data[field] = data[field]
                
        if 'discharge_notes' in data:
            update_fields.append("notes = :notes")
            update_data['notes'] = data['discharge_notes']
        
        if not update_fields:
            return jsonify({'error': '没有提供要更新的字段'}), 400
            
        update_data.update({
            'admission_id': admission_id,
            'doctor_id': doctor['id']
        })
        
        Database.execute(f"""
            UPDATE admissions 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = :admission_id 
            AND doctor_id = :doctor_id
            AND is_deleted = FALSE
        """, update_data)
        
        return jsonify({'message': '入院记录更新成功'})
        
    except Exception as e:
        print(f"Error updating admission: {str(e)}")
        return jsonify({'error': '更新入院记录失败'}), 500

@bp.route('/doctor/patient/<int:patient_id>/admissions', methods=['GET'])
@doctor_required
def get_patient_admissions(user_id, patient_id):
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
            
        # 验证患者是否存在且与该医生关联
        patient = Database.fetch_one("""
            SELECT p.id 
            FROM patients p
            JOIN patient_doctor pd ON p.id = pd.patient_id
            WHERE p.id = :patient_id AND pd.doctor_id = :doctor_id
        """, {
            'patient_id': patient_id,
            'doctor_id': doctor['id']
        })
        
        if not patient:
            return jsonify({'error': '无权查看此患者的入院记录'}), 403
            
        # 获取入院记录
        admissions = Database.fetch_all("""
            SELECT 
                a.*,
                w.room_number,
                w.ward_type
            FROM admissions a
            JOIN wards w ON a.ward_id = w.id
            WHERE a.patient_id = :patient_id 
            AND a.doctor_id = :doctor_id
            ORDER BY a.admission_date DESC
        """, {
            'patient_id': patient_id,
            'doctor_id': doctor['id']
        })
        
        return jsonify(admissions or []), 200
        
    except Exception as e:
        print(f"Error getting patient admissions: {str(e)}")
        return jsonify({'error': '获取入院记录失败'}), 500 
    
    
@bp.route('/doctor/patients', methods=['GET'])
@doctor_required
def get_all_patients(user_id):
    """获取所有患者的列表，包括完整的患者信息"""
    try:
        # 获取所有患者列表，包含完整信息
        patients = Database.fetch_all("""
            SELECT 
                id,
                name,
                birth_date,
                gender,
                contact,
                address,
                medical_history
            FROM patients
            ORDER BY name ASC
        """)
        
        # 确保返回空列表而不是 None
        return jsonify(patients or []), 200
        
    except Exception as e:
        print(f"Error getting all patients: {str(e)}")
        return jsonify({'error': '获取患者列表失败'}), 500



@bp.route('/doctor/patients/<int:patient_id>', methods=['GET'])
@doctor_required
def get_patient_info(user_id, patient_id):
    """获取当前医生关联的特定患者的详细信息"""
    try:
        # 获取医生ID
        doctor = Database.fetch_one("""
            SELECT id FROM doctors WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not doctor:
            return jsonify({'error': '医生信息不存在'}), 404
        
        # 获取患者信息，确保患者属于该医生
        patient = Database.fetch_one("""
            SELECT 
                p.id,
                p.name,
                p.birth_date,
                p.gender,
                p.contact,
                p.address,
                p.medical_history,
                pd.start_date as relationship_start,
                pd.notes
            FROM patients p
            JOIN patient_doctor pd ON p.id = pd.patient_id
            WHERE pd.doctor_id = :doctor_id AND p.id = :patient_id AND pd.is_deleted = FALSE
        """, {'doctor_id': doctor['id'], 'patient_id': patient_id})
        
        if not patient:
            return jsonify({'error': '未找到该患者或您无权访问该患者信息'}), 404
        
        return jsonify(patient), 200
    
    except Exception as e:
        print(f"Error getting patient info: {str(e)}")
        return jsonify({'error': '获取患者信息失败'}), 500