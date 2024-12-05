import pytest
from app import create_app
from app.utils.db import db
from flask import json
from sqlalchemy import text
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='session')
def app():
    """创建测试应用实例"""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture(scope='session')
def test_app_context(app):
    """创建测试应用上下文"""
    with app.app_context() as ctx:
        yield ctx

# 数据库初始化和清理
@pytest.fixture(scope='session', autouse=True)
def setup_database(test_app_context):
    """初始化测试数据库并在测试结束后清理"""
    # 读取 SQL 文件内容
    with open('database/Hospital_Management_System.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read()
    
    # 创建所有表
    db.session.execute(text(sql_commands))
    db.session.commit()
    
    # 生成测试密码的哈希值
    password_hash = generate_password_hash('password123')
    
    # 创建测试数据
    # 1. 创建用户
    db.session.execute(text("""
        INSERT INTO users (username, password_hash, role, email) VALUES
        (:username1, :password_hash, 'admin', 'admin@test.com'),
        (:username2, :password_hash, 'doctor', 'doctor@test.com'),
        (:username3, :password_hash, 'nurse', 'nurse@test.com'),
        (:username4, :password_hash, 'patient', 'patient@test.com')
    """), {
        'username1': 'testadmin',
        'username2': 'testdoctor',
        'username3': 'testnurse',
        'username4': 'testpatient',
        'password_hash': password_hash
    })
    db.session.commit()

    # 2. 创建科室
    db.session.execute(text("""
        INSERT INTO departments (name, description) VALUES
        ('Test Department', 'For testing')
    """))
    db.session.commit()

    # 3. 创建病房
    db.session.execute(text("""
        INSERT INTO wards (room_number, ward_type, bed_count) VALUES
        ('A101', '普通病房', 4)
    """))
    db.session.commit()

    # 4. 创建医生记录
    db.session.execute(text("""
        INSERT INTO doctors (user_id, name, birth_date, contact, email, department_id, specialization)
        SELECT id, 'Dr. ' || username, '1980-01-01', '1234567890', email, 1, 'General'
        FROM users WHERE role = 'doctor'
    """))
    db.session.commit()

    # 5. 创建护士记录
    db.session.execute(text("""
        INSERT INTO nurses (user_id, name, birth_date, contact, email, department_id, qualification)
        SELECT id, username, '1985-01-01', '1234567890', email, 1, 'RN'
        FROM users WHERE role = 'nurse'
    """))
    db.session.commit()

    # 6. 创建患者记录
    db.session.execute(text("""
        INSERT INTO patients (user_id, name, birth_date, gender, contact, address)
        SELECT id, username, '1990-01-01', 'M', '1234567890', 'Test Address'
        FROM users WHERE role = 'patient'
    """))
    db.session.commit()

    # 7. 创建医患关系
    db.session.execute(text("""
        INSERT INTO patient_doctor (patient_id, doctor_id, start_date, notes)
        SELECT p.id, d.id, '2024-01-01', 'Initial relationship'
        FROM patients p
        CROSS JOIN doctors d
        WHERE d.user_id = (SELECT id FROM users WHERE role = 'doctor' LIMIT 1)
        AND p.user_id = (SELECT id FROM users WHERE role = 'patient' LIMIT 1)
    """))
    db.session.commit()

    yield

    # 测试结束后清理数据
    db.session.execute(text("""
        DROP TABLE IF EXISTS nurse_ward_assignments CASCADE;
        DROP TABLE IF EXISTS admissions CASCADE;
        DROP TABLE IF EXISTS treatments CASCADE;
        DROP TABLE IF EXISTS patient_doctor CASCADE;
        DROP TABLE IF EXISTS patients CASCADE;
        DROP TABLE IF EXISTS nurses CASCADE;
        DROP TABLE IF EXISTS doctors CASCADE;
        DROP TABLE IF EXISTS wards CASCADE;
        DROP TABLE IF EXISTS departments CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
    """))
    db.session.commit()

# 认证相关测试
class TestAuth:
    def test_register_doctor(self, client):
        """测试医生注册"""
        response = client.post('/auth/register', json={
            'username': 'newdoctor',
            'password': 'password123',
            'role': 'doctor',
            'email': 'newdoctor@test.com',
            'doctor_info': {
                'name': 'Dr. New',
                'birth_date': '1980-01-01',
                'contact': '1234567890',
                'department_id': 1,
                'specialization': 'General'
            }
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert 'role_id' in data
        assert data['role'] == 'doctor'

    def test_register_nurse(self, client):
        """测试护士注册"""
        response = client.post('/auth/register', json={
            'username': 'newnurse',
            'password': 'password123',
            'role': 'nurse',
            'email': 'newnurse@test.com',
            'nurse_info': {
                'name': 'Nurse New',
                'birth_date': '1985-01-01',
                'contact': '1234567890',
                'department_id': 1,
                'qualification': 'RN'
            }
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert 'role_id' in data
        assert data['role'] == 'nurse'

    def test_register_patient(self, client):
        """测试患者注册"""
        response = client.post('/auth/register', json={
            'username': 'newpatient',
            'password': 'password123',
            'role': 'patient',
            'email': 'newpatient@test.com',
            'patient_info': {
                'name': 'Patient New',
                'birth_date': '1990-01-01',
                'gender': 'M',
                'contact': '1234567890',
                'address': 'Test Address',
                'medical_history': 'None'
            }
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert 'role_id' in data
        assert data['role'] == 'patient'

    def test_register_missing_role_info(self, client):
        """测试缺少角色信息的注册"""
        response = client.post('/auth/register', json={
            'username': 'testdoctor2',
            'password': 'password123',
            'role': 'doctor',
            'email': 'testdoctor2@test.com'
        })
        
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == '缺少医生相关信息'

    def test_register_invalid_role(self, client):
        """测试无效角色的注册"""
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123',
            'role': 'invalid_role',
            'email': 'test@test.com'
        })
        
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == '无效的用户角色'

    def test_login_after_register(self, client):
        """测试注册后登录"""
        # 先注册一个医生
        register_response = client.post('/auth/register', json={
            'username': 'testdoctor3',
            'password': 'password123',
            'role': 'doctor',
            'email': 'testdoctor3@test.com',
            'doctor_info': {
                'name': 'Dr. Test3',
                'birth_date': '1980-01-01',
                'contact': '1234567890',
                'department_id': 1,
                'specialization': 'General'
            }
        })
        assert register_response.status_code == 201
        
        # 然后尝试登录
        login_response = client.post('/auth/login', json={
            'username': 'testdoctor3',
            'password': 'password123'
        })
        
        assert login_response.status_code == 200
        data = json.loads(login_response.data)
        assert 'token' in data
        assert data['role'] == 'doctor'

    def test_register_duplicate_username(self, client):
        """测试重复用户名注册"""
        # 第一次注册
        response1 = client.post('/auth/register', json={
            'username': 'testuser4',
            'password': 'password123',
            'role': 'patient',
            'email': 'testuser4@test.com',
            'patient_info': {
                'name': 'Test User4',
                'birth_date': '1990-01-01',
                'gender': 'M',
                'contact': '1234567890',
                'address': 'Test Address'
            }
        })
        assert response1.status_code == 201
        
        # 尝试使用相同用户名再次注册
        response2 = client.post('/auth/register', json={
            'username': 'testuser4',
            'password': 'password123',
            'role': 'patient',
            'email': 'testuser4_2@test.com',
            'patient_info': {
                'name': 'Test User4_2',
                'birth_date': '1990-01-01',
                'gender': 'M',
                'contact': '1234567890',
                'address': 'Test Address'
            }
        })
        
        assert response2.status_code == 400
        assert json.loads(response2.data)['error'] == '用户名已存在'

class TestPasswordChange:
    @pytest.fixture
    def auth_headers(self, client):
        """获取认证头"""
        # 使用已存在的测试用户（在 setup_database 中创建的）
        response = client.post('/auth/login', json={
            'username': 'testdoctor',  # 使用已存在的测试用户
            'password': 'password123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        token = data['token']
        
        return {'Authorization': f'Bearer {token}'}

    def test_change_password_success(self, client, auth_headers):
        """测试成功修改密码"""
        # 修改密码
        response = client.post('/auth/change-password', json={
            'old_password': 'password123',  # 使用原始密码
            'new_password': 'newpassword123'
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == '密码修改成功'
        
        # 尝试使用旧密码登录（应该失败）
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        assert response.status_code == 401
        
        # 使用新密码登录（应该成功）
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'newpassword123'
        })
        assert response.status_code == 200
        assert 'token' in json.loads(response.data)

        # 恢复原始密码（为了不影响其他测试）
        response = client.post('/auth/change-password', json={
            'old_password': 'newpassword123',
            'new_password': 'password123'
        }, headers={'Authorization': f'Bearer {json.loads(response.data)["token"]}'})
        assert response.status_code == 200

    def test_change_password_wrong_old_password(self, client, auth_headers):
        """测试使用错误的旧密码"""
        response = client.post('/auth/change-password', json={
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }, headers=auth_headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == '旧密码错误'

    def test_change_password_missing_fields(self, client, auth_headers):
        """测试缺少必填字段"""
        # 缺少旧密码
        response = client.post('/auth/change-password', json={
            'new_password': 'newpassword123'
        }, headers=auth_headers)
        
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == '请提供旧密码和新密码'
        
        # 缺少新密码
        response = client.post('/auth/change-password', json={
            'old_password': 'password123'
        }, headers=auth_headers)
        
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == '请提供旧密码和新密码'

    def test_change_password_unauthorized(self, client):
        """测试未登录时修改密码"""
        response = client.post('/auth/change-password', json={
            'old_password': 'password123',
            'new_password': 'newpassword123'
        })
        
        assert response.status_code == 401
        assert json.loads(response.data)['error'] == '未授权访问'

    def test_change_password_invalid_token(self, client):
        """测试使用无效的token"""
        response = client.post('/auth/change-password', json={
            'old_password': 'password123',
            'new_password': 'newpassword123'
        }, headers={'Authorization': 'Bearer invalid_token'})
        
        assert response.status_code == 401
        assert json.loads(response.data)['error'] == '未授权访问'
  