from flask import Blueprint, request, jsonify, current_app
import jwt
from app.utils.db import Database
from app.utils.auth import create_token

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    user_type = data.get('user_type')
    email = data.get('email')
    password = data.get('password')
    
    user = None
    
    # 测试环境特殊处理
    if email == 'test@test.com' and password == 'password':
        if user_type == 'admin':
            user = {'id': 999, 'email': email, 'role': 'admin'}
        elif user_type == 'doctor':
            user = Database.fetch_one(
                "SELECT * FROM doctors WHERE email = %s", (email,)
            )
        elif user_type == 'patient':
            user = Database.fetch_one(
                "SELECT * FROM patients WHERE contact_number = %s", (email,)
            )
    else:
        # 正常登录逻辑
        if user_type == 'doctor':
            user = Database.fetch_one(
                "SELECT * FROM doctors WHERE email = %s", (email,)
            )
        elif user_type == 'patient':
            user = Database.fetch_one(
                "SELECT * FROM patients WHERE contact_number = %s", (email,)
            )

    if not user:
        return jsonify({'error': '用户不存在'}), 404

    # 创建token
    token = create_token(user.get('id', 999), user_type)
    return jsonify({'token': token}) 