from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, UTC

class AuthError(Exception):
    """认证错误异常类"""
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    """从请求头中获取token"""
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError('未提供认证令牌', 401)
    
    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError('认证格式错误。应使用Bearer token', 401)
    elif len(parts) == 1:
        raise AuthError('未提供token', 401)
    elif len(parts) > 2:
        raise AuthError('认证格式错误', 401)
    
    token = parts[1]
    return token

def create_token(user_id, role):
    """创建JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(UTC) + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token, required_role):
    """验证token并检查用户角色"""
    try:
        payload = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        
        user_id = payload.get('user_id')
        user_role = payload.get('role')
        
        if not user_id or not user_role:
            raise AuthError('无效的token', 401)
            
        if user_role != required_role:
            raise AuthError('权限不足', 403)
            
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise AuthError('token已过期', 401)
    except jwt.InvalidTokenError:
        raise AuthError('无效的token', 401)

def requires_auth(role):
    """认证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                token = get_token_auth_header()
                user_id = verify_token(token, role)
                return f(user_id, *args, **kwargs)
            except AuthError as e:
                return jsonify({'error': e.error}), e.status_code
        return decorated
    return decorator

# 角色特定的装饰器
def admin_required(f):
    return requires_auth('admin')(f)

def doctor_required(f):
    return requires_auth('doctor')(f)

def patient_required(f):
    return requires_auth('patient')(f) 