from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, UTC

def generate_token(user_id, role):
    """生成 JWT 令牌"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(UTC) + timedelta(days=1),  # 令牌有效期1天
        'iat': datetime.now(UTC)
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_token():
    """验证 JWT 令牌"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
        
    try:
        token = auth_header.split(' ')[1]  # Bearer token
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        payload = verify_token()
        if not payload:
            return jsonify({'error': '请先登录'}), 401
        return f(payload['user_id'], *args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = verify_token()
            if not payload:
                return jsonify({'error': '请先登录'}), 401
            if payload['role'] not in allowed_roles:
                return jsonify({'error': '权限不足'}), 403
            return f(payload['user_id'], *args, **kwargs)
        return decorated_function
    return decorator

# 简化的角色装饰器
def admin_required(f):
    return role_required(['Admin'])(f)

def doctor_required(f):
    return role_required(['Doctor', 'Admin'])(f)

def nurse_required(f):
    return role_required(['Nurse', 'Admin'])(f)

def patient_required(f):
    return role_required(['Patient'])(f) 