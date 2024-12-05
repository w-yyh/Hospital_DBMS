from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import nurse_required
from datetime import datetime

bp = Blueprint('nurse', __name__)
# 已实现功能：
# 1. 获取护士个人信息
# 2. 创建护士个人信息
# 3. 更新护士个人信息
# 4. 删除护士个人信息
# 5. 获取护士负责的病房和患者信息

@bp.route('/nurse/profile/<int:nurse_id>', methods=['GET'])
@nurse_required
def get_nurse_profile(user_id, nurse_id):# 这里不知道为啥，user_id 和 nurse_id 指的都是 user_id 之后就把id替换成user_id了
    try:
        # 获取护士ID
        nurse = Database.fetch_one("""
            SELECT user_id FROM nurses WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not nurse:
            return jsonify({'error': '护士信息不存在'}), 404
            
            
        # 获取护士详细信息
        nurse_info = Database.fetch_one("""
            SELECT n.*, d.name as department_name 
            FROM nurses n
            LEFT JOIN departments d ON n.department_id = d.id
            WHERE n.user_id = :user_id AND n.is_deleted = FALSE
        """, {'user_id': user_id})
        
        if not nurse_info:
            return jsonify({'error': '护士不存在'}), 404
            
        return jsonify(nurse_info), 200
        
    except Exception as e:
        print(f"Error getting nurse profile: {str(e)}")
        return jsonify({'error': '获取护士信息失败'}), 500


@bp.route('/nurse', methods=['POST'])
@nurse_required
def create_nurse(user_id):
    data = request.get_json()
    required_fields = ['name', 'birth_date', 'contact', 'email', 'department_id', 'qualification']
    
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
            
        # 创建护士记录
        nurse_id = Database.execute("""
            INSERT INTO nurses (
                user_id, name, birth_date, contact, 
                email, department_id, qualification
            ) VALUES (
                :user_id, :name, :birth_date, :contact,
                :email, :department_id, :qualification
            ) RETURNING id
        """, {
            'user_id': user_id,
            'name': data['name'],
            'birth_date': data['birth_date'],
            'contact': data['contact'],
            'email': data['email'],
            'department_id': data['department_id'],
            'qualification': data['qualification']
        })
        
        return jsonify({
            'message': '护士记录创建成功',
            'nurse_id': nurse_id
        }), 201
        
    except Exception as e:
        print(f"Error creating nurse: {str(e)}")
        return jsonify({'error': '创建护士记录失败'}), 500

@bp.route('/nurse/<int:nurse_id>', methods=['PUT'])
@nurse_required
def update_nurse(user_id, nurse_id):
    if user_id != nurse_id:
        return jsonify({'error': '无权修改此护士信息'}), 403
        
    data = request.get_json()
    allowed_fields = ['name', 'birth_date', 'contact', 'email', 'qualification']
    update_fields = []
    values = []
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f"{field} = %s")
            if field == 'birth_date':
                try:
                    birth_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                    values.append(birth_date)
                except ValueError:
                    return jsonify({'error': '出生日期格式无效'}), 400
            else:
                values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': '没有提供要更新的字段'}), 400
        
    values.append(nurse_id)
    
    try:
        Database.execute(f"""
            UPDATE nurses 
            SET {', '.join(update_fields)}, updated_at = NOW()
            WHERE nurse_id = %s AND is_deleted = FALSE
        """, tuple(values))
        
        return jsonify({'message': '护士信息更新成功'})
    except Exception as e:
        return jsonify({'error': f'更新护士信息失败: {str(e)}'}), 500

@bp.route('/nurse/<int:nurse_id>', methods=['DELETE'])
@nurse_required
def delete_nurse(user_id, nurse_id):
    if user_id != nurse_id:
        return jsonify({'error': '无权删除此护士信息'}), 403
    
    try:
        # 检查是否有正在负责的病房或患者
        assigned_wards = Database.fetch_one("""
            SELECT COUNT(*) as count 
            FROM nurse_ward_assignments 
            WHERE nurse_id = %s AND end_date IS NULL
        """, (nurse_id,))
        
        if assigned_wards['count'] > 0:
            return jsonify({'error': '该护士还有正在负责的病房，无法删除'}), 400
            
        # 软删除护士记录
        Database.execute("""
            UPDATE nurses 
            SET is_deleted = TRUE, deleted_at = NOW() 
            WHERE nurse_id = %s
        """, (nurse_id,))
        
        return jsonify({'message': '护士记录已删除'})
    except Exception as e:
        return jsonify({'error': f'删除护士失败: {str(e)}'}), 500

@bp.route('/nurse/<int:nurse_id>/wards', methods=['GET'])
@nurse_required
def get_nurse_wards(user_id, nurse_id):
    try:
        # 获取护士ID
        nurse = Database.fetch_one("""
            SELECT id FROM nurses WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not nurse:
            return jsonify({'error': '护士信息不存在'}), 404
            
        # 获取护士负责的病房
        wards = Database.fetch_all("""
            SELECT 
                w.*,
                nwa.shift,
                nwa.start_date,
                nwa.end_date
            FROM wards w
            JOIN nurse_ward_assignments nwa ON w.id = nwa.ward_id
            WHERE nwa.nurse_id = :nurse_id
            ORDER BY nwa.start_date DESC
        """, {'nurse_id': nurse['id']})
        
        return jsonify(wards or []), 200
        
    except Exception as e:
        print(f"Error getting nurse wards: {str(e)}")
        return jsonify({'error': '获取病房列表失败'}), 500

@bp.route('/nurse/<int:nurse_id>/patients', methods=['GET'])
@nurse_required
def get_nurse_patients(user_id, nurse_id):
    if user_id != nurse_id:
        return jsonify({'error': '无权访问此信息'}), 403
        
    try:
        # 获取护士负责病房中的患者信息
        patients = Database.fetch_all("""
            SELECT DISTINCT p.*, 
                   w.room_number, w.ward_type,
                   a.admission_date
            FROM nurse_ward_assignments nwa
            JOIN wards w ON nwa.ward_id = w.ward_id
            JOIN admissions a ON w.ward_id = a.ward_id
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE nwa.nurse_id = %s 
                AND w.is_deleted = FALSE
                AND p.is_deleted = FALSE
                AND a.discharge_date IS NULL
                AND (nwa.end_date IS NULL OR nwa.end_date > NOW())
            ORDER BY w.room_number, p.name
        """, (nurse_id,))
        
        return jsonify(patients)
    except Exception as e:
        return jsonify({'error': f'获取患者信息失败: {str(e)}'}), 500

@bp.route('/nurse/<int:nurse_id>/schedule', methods=['PUT'])
@nurse_required
def update_nurse_schedule(user_id, nurse_id):
    try:
        # 获取护士ID
        nurse = Database.fetch_one("""
            SELECT id FROM nurses WHERE user_id = :user_id
        """, {'user_id': user_id})
        
        if not nurse:
            return jsonify({'error': '护士信息不存在'}), 404
            
        data = request.get_json()
        required_fields = ['ward_id', 'shift']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400
                
        # 验证病房是否存在
        ward = Database.fetch_one("""
            SELECT id FROM wards WHERE id = :ward_id
        """, {'ward_id': data['ward_id']})
        
        if not ward:
            return jsonify({'error': '指定的病房不存在'}), 404
            
        # 先结束当前的排班
        Database.execute("""
            UPDATE nurse_ward_assignments 
            SET end_date = CURRENT_DATE
            WHERE nurse_id = :nurse_id 
            AND end_date IS NULL
        """, {'nurse_id': nurse['id']})
        
        # 创建新的排班记录
        Database.execute("""
            INSERT INTO nurse_ward_assignments (
                nurse_id, ward_id, shift, start_date
            ) VALUES (
                :nurse_id, :ward_id, :shift, CURRENT_DATE
            )
        """, {
            'nurse_id': nurse['id'],
            'ward_id': data['ward_id'],
            'shift': data['shift']
        })
        
        return jsonify({'message': '排班信息更新成功'})
        
    except Exception as e:
        print(f"Error updating nurse schedule: {str(e)}")
        return jsonify({'error': '更新排班信息失败'}), 500 