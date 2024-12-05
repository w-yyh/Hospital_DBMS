from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import admin_required
from datetime import datetime

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


# 科室管理相关路由
@bp.route('/admin/department/<int:doctor_id>/assign', methods=['PUT'])
@admin_required
def assign_department(user_id, doctor_id):
    data = request.get_json()
    if 'department_id' not in data:
        return jsonify({'error': '缺少department_id字段'}), 400
        
    try:
        # 验证科室是否存在
        department = Database.fetch_one("""
            SELECT department_id, department_name 
            FROM departments 
            WHERE department_id = %s
        """, (data['department_id'],))
        
        if not department:
            return jsonify({'error': '指定的科室不存在'}), 400
            
        # 更新医生的科室
        Database.execute("""
            UPDATE doctors 
            SET department_id = %s, updated_at = NOW()
            WHERE doctor_id = %s AND is_deleted = FALSE
        """, (data['department_id'], doctor_id))
        
        return jsonify({
            'message': '科室分配成功',
            'department': department
        })
    except Exception as e:
        return jsonify({'error': f'科室分配失败: {str(e)}'}), 500

@bp.route('/admin/department/<int:department_id>/doctors', methods=['GET'])
@admin_required
def get_department_doctors(user_id, department_id):
    try:
        # 验证科室是否存在
        department = Database.fetch_one("""
            SELECT department_id, department_name 
            FROM departments 
            WHERE department_id = %s
        """, (department_id,))
        
        if not department:
            return jsonify({'error': '指定的科室不存在'}), 404
            
        # 获取科室下的所有医生
        doctors = Database.fetch_all("""
            SELECT d.doctor_id, d.name, d.specialization, d.contact, d.email
            FROM doctors d
            WHERE d.department_id = %s 
            AND d.is_deleted = FALSE
            ORDER BY d.name
        """, (department_id,))
        
        return jsonify({
            'department': department,
            'doctors': doctors
        })
    except Exception as e:
        return jsonify({'error': f'获取科室医生列表失败: {str(e)}'}), 500

@bp.route('/admin/departments', methods=['GET'])
@admin_required
def get_departments(user_id):
    try:
        departments = Database.fetch_all("""
            SELECT d.department_id, d.department_name,
                   COUNT(doc.doctor_id) as doctor_count
            FROM departments d
            LEFT JOIN doctors doc ON d.department_id = doc.department_id 
                AND doc.is_deleted = FALSE
            GROUP BY d.department_id, d.department_name
            ORDER BY d.department_name
        """)
        
        return jsonify(departments)
    except Exception as e:
        return jsonify({'error': f'获取科室列表失败: {str(e)}'}), 500

@bp.route('/admin/department/transfer', methods=['POST'])
@admin_required
def transfer_doctors(user_id):
    data = request.get_json()
    if not all(key in data for key in ['doctor_ids', 'target_department_id']):
        return jsonify({'error': '缺少必要的参数'}), 400
        
    try:
        # 验证目标科室是否存在
        target_dept = Database.fetch_one("""
            SELECT department_id 
            FROM departments 
            WHERE department_id = %s
        """, (data['target_department_id'],))
        
        if not target_dept:
            return jsonify({'error': '目标科室不存在'}), 400
            
        # 批量转移医生到新科室
        Database.execute("""
            UPDATE doctors 
            SET department_id = %s, updated_at = NOW()
            WHERE doctor_id = ANY(%s) AND is_deleted = FALSE
        """, (data['target_department_id'], data['doctor_ids']))
        
        return jsonify({'message': '医生科室转移成功'})
    except Exception as e:
        return jsonify({'error': f'医生科室转移失败: {str(e)}'}), 500

# 科室基础信息管理
@bp.route('/admin/department', methods=['POST'])
@admin_required
def create_department(user_id):
    data = request.get_json()
    required_fields = ['name', 'description']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 检查科室名是否已存在
        existing = Database.fetch_one("""
            SELECT id FROM departments 
            WHERE name = :name
        """, {'name': data['name']})
        
        if existing:
            return jsonify({'error': '科室名已存在'}), 400
            
        # 创建科室
        department_id = Database.execute("""
            INSERT INTO departments (name, description)
            VALUES (:name, :description)
            RETURNING id
        """, {
            'name': data['name'],
            'description': data['description']
        })
        
        return jsonify({
            'message': '科室创建成功',
            'department_id': department_id
        }), 201
        
    except Exception as e:
        print(f"Error creating department: {str(e)}")
        return jsonify({'error': '创建科室失败'}), 500

@bp.route('/admin/department/<int:department_id>', methods=['GET'])
@admin_required
def get_department(user_id, department_id):
    try:
        # 获取科室信息及其医生数量
        department = Database.fetch_one("""
            SELECT d.*, 
                   COUNT(doc.doctor_id) as doctor_count
            FROM departments d
            LEFT JOIN doctors doc ON d.department_id = doc.department_id 
                AND doc.is_deleted = FALSE
            WHERE d.department_id = %s AND d.is_deleted = FALSE
            GROUP BY d.department_id
        """, (department_id,))
        
        if not department:
            return jsonify({'error': '科室不存在'}), 404
            
        return jsonify(department)
    except Exception as e:
        return jsonify({'error': f'获取科室信息失败: {str(e)}'}), 500

@bp.route('/admin/departments', methods=['GET'])
@admin_required
def get_all_departments(user_id):
    try:
        # 获取所有科室信息及其医生数量
        departments = Database.fetch_all("""
            SELECT d.*, 
                   COUNT(doc.doctor_id) as doctor_count
            FROM departments d
            LEFT JOIN doctors doc ON d.department_id = doc.department_id 
                AND doc.is_deleted = FALSE
            WHERE d.is_deleted = FALSE
            GROUP BY d.department_id
            ORDER BY d.name
        """)
        
        return jsonify(departments)
    except Exception as e:
        return jsonify({'error': f'获取科室列表失败: {str(e)}'}), 500

@bp.route('/admin/department/<int:department_id>', methods=['PUT'])
@admin_required
def update_department(user_id, department_id):
    data = request.get_json()
    allowed_fields = ['name', 'description']
    update_fields = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            if field == 'name':
                # 检查新名称是否与其他科室重复
                existing = Database.fetch_one("""
                    SELECT department_id 
                    FROM departments 
                    WHERE name = %s 
                    AND department_id != %s 
                    AND is_deleted = FALSE
                """, (data['name'], department_id))
                
                if existing:
                    return jsonify({'error': '科室名称已存在'}), 400
                    
            update_fields.append(f"{field} = %s")
            values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
        
    values.append(department_id)
    
    try:
        Database.execute(f"""
            UPDATE departments 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE department_id = %s AND is_deleted = FALSE
        """, tuple(values))
        
        return jsonify({'message': '科室信息更新成功'})
    except Exception as e:
        return jsonify({'error': f'更新科室信息失败: {str(e)}'}), 500

@bp.route('/admin/department/<int:department_id>', methods=['DELETE'])
@admin_required
def delete_department(user_id, department_id):
    try:
        # 检查科室下是否有医生
        doctor_count = Database.fetch_one("""
            SELECT COUNT(*) as count 
            FROM doctors 
            WHERE department_id = %s AND is_deleted = FALSE
        """, (department_id,))
        
        if doctor_count['count'] > 0:
            return jsonify({
                'error': '该科室下还有医生，无法删除。请先将医生转移到其他科室。',
                'doctor_count': doctor_count['count']
            }), 400
            
        # 软删除科室
        Database.execute("""
            UPDATE departments 
            SET is_deleted = TRUE, deleted_at = NOW()
            WHERE department_id = %s AND is_deleted = FALSE
        """, (department_id,))
        
        return jsonify({'message': '科室删除成功'})
    except Exception as e:
        return jsonify({'error': f'删除科室失败: {str(e)}'}), 500

# 科室统计信息
@bp.route('/admin/department/<int:department_id>/stats', methods=['GET'])
@admin_required
def get_department_stats(user_id, department_id):
    try:
        stats = Database.fetch_one("""
            SELECT 
                d.name as department_name,
                COUNT(DISTINCT doc.doctor_id) as doctor_count,
                COUNT(DISTINCT pd.patient_id) as patient_count,
                COUNT(DISTINCT t.treatment_id) as treatment_count
            FROM departments d
            LEFT JOIN doctors doc ON d.department_id = doc.department_id 
                AND doc.is_deleted = FALSE
            LEFT JOIN patient_doctor pd ON doc.doctor_id = pd.doctor_id
            LEFT JOIN treatments t ON doc.doctor_id = t.doctor_id 
                AND t.created_at >= NOW() - INTERVAL '30 days'
            WHERE d.department_id = %s AND d.is_deleted = FALSE
            GROUP BY d.department_id, d.name
        """, (department_id,))
        
        if not stats:
            return jsonify({'error': '科室不存在'}), 404
            
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'获取科室统计信息失败: {str(e)}'}), 500

# 病房信息管理相关路由
@bp.route('/admin/ward', methods=['POST'])
@admin_required
def create_ward(user_id):
    data = request.get_json()
    required_fields = ['room_number', 'ward_type', 'bed_count']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 检查房间号是否已存在
        existing = Database.fetch_one("""
            SELECT id FROM wards 
            WHERE room_number = :room_number
        """, {'room_number': data['room_number']})
        
        if existing:
            return jsonify({'error': '房间号已存在'}), 400
            
        # 创建病房
        ward_id = Database.execute("""
            INSERT INTO wards (room_number, ward_type, bed_count)
            VALUES (:room_number, :ward_type, :bed_count)
            RETURNING id
        """, {
            'room_number': data['room_number'],
            'ward_type': data['ward_type'],
            'bed_count': data['bed_count']
        })
        
        return jsonify({
            'message': '病房创建成功',
            'ward_id': ward_id
        }), 201
        
    except Exception as e:
        print(f"Error creating ward: {str(e)}")
        return jsonify({'error': '创建病房失败'}), 500

@bp.route('/admin/ward/<int:ward_id>', methods=['GET'])
@admin_required
def get_ward(user_id, ward_id):
    try:
        # 获取病房信息及当前入住情况
        ward = Database.fetch_one("""
            SELECT w.*, 
                   COUNT(DISTINCT a.admission_id) as current_patients,
                   w.bed_count - COUNT(DISTINCT a.admission_id) as available_beds
            FROM wards w
            LEFT JOIN admissions a ON w.ward_id = a.ward_id 
                AND a.discharge_date IS NULL
            WHERE w.ward_id = %s AND w.is_deleted = FALSE
            GROUP BY w.ward_id
        """, (ward_id,))
        
        if not ward:
            return jsonify({'error': '病房不存在'}), 404
            
        return jsonify(ward)
    except Exception as e:
        return jsonify({'error': f'获取病房信息失败: {str(e)}'}), 500

@bp.route('/admin/wards', methods=['GET'])
@admin_required
def get_all_wards(user_id):
    try:
        # 获取所有病房信息及入住情况
        wards = Database.fetch_all("""
            SELECT w.*, 
                   COUNT(DISTINCT a.admission_id) as current_patients,
                   w.bed_count - COUNT(DISTINCT a.admission_id) as available_beds
            FROM wards w
            LEFT JOIN admissions a ON w.ward_id = a.ward_id 
                AND a.discharge_date IS NULL
            WHERE w.is_deleted = FALSE
            GROUP BY w.ward_id
            ORDER BY w.room_number
        """)
        
        return jsonify(wards)
    except Exception as e:
        return jsonify({'error': f'获取病房列表失败: {str(e)}'}), 500

@bp.route('/admin/ward/<int:ward_id>', methods=['PUT'])
@admin_required
def update_ward(user_id, ward_id):
    data = request.get_json()
    allowed_fields = ['room_number', 'ward_type', 'bed_count', 'description', 'status']
    update_fields = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            if field == 'room_number':
                # 检查房间号是否与其他病房重复
                existing = Database.fetch_one("""
                    SELECT ward_id 
                    FROM wards 
                    WHERE room_number = %s 
                    AND ward_id != %s 
                    AND is_deleted = FALSE
                """, (data['room_number'], ward_id))
                
                if existing:
                    return jsonify({'error': '房间号已存在'}), 400
            elif field == 'ward_type':
                # 验证病房类型
                valid_types = ['普通病房', 'ICU', '手术室', 'VIP病房']
                if data['ward_type'] not in valid_types:
                    return jsonify({'error': '无效的病房类型'}), 400
            elif field == 'bed_count':
                # 检查是否有足够的空床位进行调整
                current_patients = Database.fetch_one("""
                    SELECT COUNT(*) as count
                    FROM admissions
                    WHERE ward_id = %s AND discharge_date IS NULL
                """, (ward_id,))
                
                if current_patients['count'] > data['bed_count']:
                    return jsonify({
                        'error': '当前入住人数超过新的床位数，无法调整',
                        'current_patients': current_patients['count']
                    }), 400
                    
            update_fields.append(f"{field} = %s")
            values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
        
    values.append(ward_id)
    
    try:
        Database.execute(f"""
            UPDATE wards 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE ward_id = %s AND is_deleted = FALSE
        """, tuple(values))
        
        return jsonify({'message': '病房信息更新成功'})
    except Exception as e:
        return jsonify({'error': f'更新病房信息失败: {str(e)}'}), 500

@bp.route('/admin/ward/<int:ward_id>', methods=['DELETE'])
@admin_required
def delete_ward(user_id, ward_id):
    try:
        # 检查病房是否有当前住院患者
        current_patients = Database.fetch_one("""
            SELECT COUNT(*) as count
            FROM admissions
            WHERE ward_id = %s AND discharge_date IS NULL
        """, (ward_id,))
        
        if current_patients['count'] > 0:
            return jsonify({
                'error': '该病房当前有住院患者，无法删除',
                'current_patients': current_patients['count']
            }), 400
            
        # 软删除病房
        Database.execute("""
            UPDATE wards 
            SET is_deleted = TRUE, deleted_at = NOW()
            WHERE ward_id = %s AND is_deleted = FALSE
        """, (ward_id,))
        
        return jsonify({'message': '病房删除成功'})
    except Exception as e:
        return jsonify({'error': f'删除病房失败: {str(e)}'}), 500

# 病房统计信息
@bp.route('/admin/ward/stats', methods=['GET'])
@admin_required
def get_ward_stats(user_id):
    try:
        stats = Database.fetch_one("""
            SELECT 
                COUNT(*) as total_wards,
                SUM(bed_count) as total_beds,
                SUM(bed_count) - COUNT(DISTINCT a.admission_id) as available_beds,
                COUNT(DISTINCT a.admission_id) as occupied_beds,
                ROUND(COUNT(DISTINCT a.admission_id)::FLOAT / SUM(bed_count) * 100, 2) as occupancy_rate
            FROM wards w
            LEFT JOIN admissions a ON w.ward_id = a.ward_id 
                AND a.discharge_date IS NULL
            WHERE w.is_deleted = FALSE
        """)
        
        # 按病房类型统计
        type_stats = Database.fetch_all("""
            SELECT 
                w.ward_type,
                COUNT(*) as ward_count,
                SUM(w.bed_count) as total_beds,
                COUNT(DISTINCT a.admission_id) as occupied_beds
            FROM wards w
            LEFT JOIN admissions a ON w.ward_id = a.ward_id 
                AND a.discharge_date IS NULL
            WHERE w.is_deleted = FALSE
            GROUP BY w.ward_type
            ORDER BY w.ward_type
        """)
        
        return jsonify({
            'overall_stats': stats,
            'type_stats': type_stats
        })
    except Exception as e:
        return jsonify({'error': f'获取病房统计信息失败: {str(e)}'}), 500

# 护士病房分配相关路由
@bp.route('/admin/nurse-assignment', methods=['POST'])
@admin_required
def assign_nurse_to_ward(user_id):
    data = request.get_json()
    required_fields = ['nurse_id', 'ward_id', 'start_date']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 验证护士是否存在
        nurse = Database.fetch_one("""
            SELECT id FROM nurses WHERE id = :nurse_id
        """, {'nurse_id': data['nurse_id']})
        
        if not nurse:
            return jsonify({'error': '护士不存在'}), 404
            
        # 验证病房是否存在
        ward = Database.fetch_one("""
            SELECT id FROM wards WHERE id = :ward_id
        """, {'ward_id': data['ward_id']})
        
        if not ward:
            return jsonify({'error': '病房不存在'}), 404
            
        # 创建分配记录
        assignment_id = Database.execute("""
            INSERT INTO nurse_ward_assignments (
                nurse_id, ward_id, start_date, shift
            ) VALUES (
                :nurse_id, :ward_id, :start_date, :shift
            ) RETURNING id
        """, {
            'nurse_id': data['nurse_id'],
            'ward_id': data['ward_id'],
            'start_date': data['start_date'],
            'shift': data.get('shift', 'day')
        })
        
        return jsonify({
            'message': '护士分配成功',
            'assignment_id': assignment_id
        }), 201
        
    except Exception as e:
        print(f"Error assigning nurse: {str(e)}")
        return jsonify({'error': '护士分配失败'}), 500

@bp.route('/admin/ward/<int:ward_id>/nurses', methods=['GET'])
@admin_required
def get_ward_nurses(user_id, ward_id):
    try:
        # 获取病房当前的护士分配情况
        nurses = Database.fetch_all("""
            SELECT n.*, 
                   nwa.start_date, nwa.end_date,
                   d.name as department_name
            FROM nurse_ward_assignments nwa
            JOIN nurses n ON nwa.nurse_id = n.nurse_id
            LEFT JOIN departments d ON n.department_id = d.department_id
            WHERE nwa.ward_id = %s 
                AND n.is_deleted = FALSE
                AND (nwa.end_date IS NULL OR nwa.end_date >= CURRENT_DATE)
            ORDER BY nwa.start_date DESC
        """, (ward_id,))
        
        return jsonify(nurses)
    except Exception as e:
        return jsonify({'error': f'获取病房护士列表失败: {str(e)}'}), 500

@bp.route('/admin/nurse-assignment/<int:assignment_id>', methods=['PUT'])
@admin_required
def update_nurse_assignment(user_id, assignment_id):
    data = request.get_json()
    allowed_fields = ['ward_id', 'start_date', 'end_date']
    update_fields = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            if field in ['start_date', 'end_date']:
                try:
                    date_value = datetime.strptime(data[field], '%Y-%m-%d').date()
                    values.append(date_value)
                except ValueError:
                    return jsonify({'error': f'{field}日期格式无效'}), 400
            else:
                values.append(data[field])
            update_fields.append(f"{field} = %s")
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
        
    values.append(assignment_id)
    
    try:
        # 验证分配记录是否存在
        assignment = Database.fetch_one("""
            SELECT * FROM nurse_ward_assignments
            WHERE assignment_id = %s
        """, (assignment_id,))
        
        if not assignment:
            return jsonify({'error': '分配记录不存在'}), 404
            
        # 更新分配记录
        Database.execute(f"""
            UPDATE nurse_ward_assignments 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE assignment_id = %s
        """, tuple(values))
        
        return jsonify({'message': '护士病房分配更新成功'})
    except Exception as e:
        return jsonify({'error': f'更新护士病房分配失败: {str(e)}'}), 500

@bp.route('/admin/nurse-assignment/<int:assignment_id>', methods=['DELETE'])
@admin_required
def delete_nurse_assignment(user_id, assignment_id):
    try:
        # 验证分配记录是否存在
        assignment = Database.fetch_one("""
            SELECT * FROM nurse_ward_assignments
            WHERE assignment_id = %s
        """, (assignment_id,))
        
        if not assignment:
            return jsonify({'error': '分配记录不存在'}), 404
            
        # 设置结束日期为当前日期而不是删除记录
        Database.execute("""
            UPDATE nurse_ward_assignments 
            SET end_date = CURRENT_DATE, updated_at = NOW()
            WHERE assignment_id = %s
        """, (assignment_id,))
        
        return jsonify({'message': '护士病房分配已终止'})
    except Exception as e:
        return jsonify({'error': f'终止护士病房分配失败: {str(e)}'}), 500

# 护士病房分配统计
@bp.route('/admin/nurse-assignment/stats', methods=['GET'])
@admin_required
def get_nurse_assignment_stats(user_id):
    try:
        # 获取总体统计信息
        stats = Database.fetch_one("""
            SELECT 
                COUNT(DISTINCT n.nurse_id) as total_nurses,
                COUNT(DISTINCT w.ward_id) as total_wards,
                COUNT(DISTINCT nwa.assignment_id) as total_assignments,
                ROUND(AVG(
                    CASE WHEN nwa.end_date IS NULL 
                    THEN 1 
                    ELSE 0 
                    END
                )::NUMERIC * 100, 2) as active_assignment_percentage
            FROM nurses n
            CROSS JOIN wards w
            LEFT JOIN nurse_ward_assignments nwa 
                ON n.nurse_id = nwa.nurse_id 
                AND w.ward_id = nwa.ward_id
            WHERE n.is_deleted = FALSE AND w.is_deleted = FALSE
        """)
        
        # 获取每个病房的护士数量
        ward_stats = Database.fetch_all("""
            SELECT 
                w.ward_id,
                w.room_number,
                w.ward_type,
                COUNT(DISTINCT nwa.nurse_id) as nurse_count
            FROM wards w
            LEFT JOIN nurse_ward_assignments nwa ON w.ward_id = nwa.ward_id
                AND (nwa.end_date IS NULL OR nwa.end_date >= CURRENT_DATE)
            WHERE w.is_deleted = FALSE
            GROUP BY w.ward_id, w.room_number, w.ward_type
            ORDER BY w.room_number
        """)
        
        return jsonify({
            'overall_stats': stats,
            'ward_stats': ward_stats
        })
    except Exception as e:
        return jsonify({'error': f'获取护士分配统计信息失败: {str(e)}'}), 500 