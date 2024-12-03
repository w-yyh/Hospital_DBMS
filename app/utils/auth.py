from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, UTC

def verify_token():
    """验证JWT令牌"""
    token = request.headers.get('Authorization')
    if not token:
        return None
        
    try:
        token = token.split(' ')[1]  # Bearer token
        payload = jwt.decode(
            token,
            current_app.config.get('SECRET_KEY', 'dev'),
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'error': '未授权访问'}), 401
            
        if payload['role'] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated_function

def doctor_required(f):
    """医生权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'error': '未授权访问'}), 401
            
        if payload['role'] != 'doctor':
            return jsonify({'error': '需要医生权限'}), 403
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated_function

def nurse_required(f):
    """护士权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'error': '未授权访问'}), 401
            
        if payload['role'] != 'nurse':
            return jsonify({'error': '需要护士权限'}), 403
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated_function

def patient_required(f):
    """患者权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'error': '未授权访问'}), 401
            
        if payload['role'] != 'patient':
            return jsonify({'error': '需要患者权限'}), 403
            
        return f(payload['user_id'], *args, **kwargs)
    return decorated_function

def generate_token(user_id, role):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(UTC) + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256') 