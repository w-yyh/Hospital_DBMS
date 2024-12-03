from flask import Blueprint, request, jsonify
from app.utils.db import Database
from app.utils.auth import generate_token, admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os

bp = Blueprint('auth', __name__)

# 用户注册
@bp.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ['username', 'password', 'role', 'email']
    
    # 验证必填字段
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必填字段: {field}'}), 400
            
    try:
        # 验证用户名是否已存在
        existing_user = Database.fetch_one("""
            SELECT id FROM users 
            WHERE username = :username
        """, {'username': data['username']})
        
        if existing_user:
            return jsonify({'error': '用户名已存在'}), 400
            
        # 验证角色是否有效
        valid_roles = ['admin', 'doctor', 'nurse', 'patient']
        if data['role'] not in valid_roles:
            return jsonify({'error': '无效的用户角色'}), 400
            
        # 创建用户记录
        password_hash = generate_password_hash(data['password'])
        result = Database.execute("""
            INSERT INTO users (username, password_hash, role, email)
            VALUES (:username, :password_hash, :role, :email)
            RETURNING id
        """, {
            'username': data['username'],
            'password_hash': password_hash,
            'role': data['role'],
            'email': data['email']
        })
        
        return jsonify({
            'message': '用户注册成功',
            'user_id': result
        }), 201
        
    except Exception as e:
        print(f"Register error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'用户注册失败: {str(e)}'}), 500

# 用户登录
@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': '请提供用户名和密码'}), 400
        
    try:
        # 获取用户信息
        user = Database.fetch_one("""
            SELECT 
                id as user_id,
                username,
                password_hash,
                role
            FROM users 
            WHERE username = :username
        """, {'username': data['username']})
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        # 验证密码
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': '密码错误'}), 401
            
        # 生成JWT令牌
        token = generate_token(user['user_id'], user['role'])
        
        return jsonify({
            'token': token,
            'user_id': user['user_id'],
            'role': user['role']
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

# 密码重置请求
@bp.route('/auth/password-reset-request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    if 'email' not in data:
        return jsonify({'error': '请提供邮箱地址'}), 400
        
    try:
        # 验证邮箱是否存在
        user = Database.fetch_one("""
            SELECT user_id, username, email 
            FROM users 
            WHERE email = %s AND is_deleted = FALSE
        """, (data['email'],))
        
        if not user:
            return jsonify({'error': '该邮箱未注册'}), 404
            
        # 生成重置令牌
        reset_token = jwt.encode(
            {
                'user_id': user['user_id'],
                'exp': datetime.utcnow() + timedelta(hours=1)
            },
            os.getenv('JWT_SECRET_KEY'),
            algorithm='HS256'
        )
        
        # 存储重置令牌
        Database.execute("""
            UPDATE users 
            SET reset_token = %s, reset_token_exp = %s
            WHERE user_id = %s
        """, (reset_token, datetime.utcnow() + timedelta(hours=1), user['user_id']))
        
        # TODO: 发送重置邮件
        # send_reset_email(user['email'], reset_token)
        
        return jsonify({'message': '密码重置链接已发送到您的邮箱'})
    except Exception as e:
        return jsonify({'error': f'密码重置请求失败: {str(e)}'}), 500

# 密码重置
@bp.route('/auth/password-reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not all(k in data for k in ['token', 'new_password']):
        return jsonify({'error': '请提供重置令牌和新密码'}), 400
        
    try:
        # 验证令牌
        payload = jwt.decode(
            data['token'],
            os.getenv('JWT_SECRET_KEY'),
            algorithms=['HS256']
        )
        
        # 检查令牌是否有效
        user = Database.fetch_one("""
            SELECT user_id 
            FROM users 
            WHERE user_id = %s 
                AND reset_token = %s 
                AND reset_token_exp > NOW()
                AND is_deleted = FALSE
        """, (payload['user_id'], data['token']))
        
        if not user:
            return jsonify({'error': '无效或已过期的重置令牌'}), 400
            
        # 更新密码
        password_hash = generate_password_hash(data['new_password'])
        Database.execute("""
            UPDATE users 
            SET password_hash = %s,
                reset_token = NULL,
                reset_token_exp = NULL,
                updated_at = NOW()
            WHERE user_id = %s
        """, (password_hash, user['user_id']))
        
        return jsonify({'message': '密码重置成功'})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': '重置令牌已过期'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': '无效的重置令牌'}), 400
    except Exception as e:
        return jsonify({'error': f'密码重置失败: {str(e)}'}), 500

# 修改密码
@bp.route('/auth/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    if not all(k in data for k in ['user_id', 'current_password', 'new_password']):
        return jsonify({'error': '请提供当前密码和新密码'}), 400
        
    try:
        # 验证用户
        user = Database.fetch_one("""
            SELECT user_id, password_hash 
            FROM users 
            WHERE user_id = %s AND is_deleted = FALSE
        """, (data['user_id'],))
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
            
        # 验证当前密码
        if not check_password_hash(user['password_hash'], data['current_password']):
            return jsonify({'error': '当前密码错误'}), 401
            
        # 更新密码
        password_hash = generate_password_hash(data['new_password'])
        Database.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = NOW()
            WHERE user_id = %s
        """, (password_hash, user['user_id']))
        
        return jsonify({'message': '密码修改成功'})
    except Exception as e:
        return jsonify({'error': f'密码修改失败: {str(e)}'}), 500

# 权限管理接口
@bp.route('/auth/roles', methods=['GET'])
@admin_required
def get_roles(user_id):
    try:
        roles = Database.fetch_all("""
            SELECT DISTINCT role, 
                   COUNT(*) as user_count
            FROM users
            WHERE is_deleted = FALSE
            GROUP BY role
        """)
        
        return jsonify(roles)
    except Exception as e:
        return jsonify({'error': f'获取角色列表失败: {str(e)}'}), 500

@bp.route('/auth/user/<int:target_user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(user_id, target_user_id):
    data = request.get_json()
    if 'role' not in data:
        return jsonify({'error': '请提供新的角色'}), 400
        
    try:
        # 验证角色是否有效
        valid_roles = ['admin', 'doctor', 'nurse', 'receptionist']
        if data['role'] not in valid_roles:
            return jsonify({'error': '无效的用户角色'}), 400
            
        # 更新用户角色
        Database.execute("""
            UPDATE users 
            SET role = %s, updated_at = NOW()
            WHERE user_id = %s AND is_deleted = FALSE
        """, (data['role'], target_user_id))
        
        return jsonify({'message': '用户角色更新成功'})
    except Exception as e:
        return jsonify({'error': f'更新用户角色失败: {str(e)}'}), 500