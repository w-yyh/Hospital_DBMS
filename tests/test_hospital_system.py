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
    def test_register(self, client):
        """测试用户注册"""
        response = client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123',
            'role': 'doctor',
            'email': 'test@example.com'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data

    def test_login(self, client):
        """测试用户登录"""
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['token'] is not None

# 医生相关测试
class TestDoctor:
    @pytest.fixture
    def auth_headers(self, client):
        """获取认证头"""
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        # 获取医生ID
        doctor = db.session.execute(text("""
            SELECT id FROM doctors 
            WHERE user_id = (SELECT id FROM users WHERE username = 'testdoctor')
        """)).fetchone()
        return {
            'Authorization': f'Bearer {token}',
            'doctor_id': doctor[0] if doctor else None
        }

    def test_create_doctor(self, client, auth_headers):
        """测试创建医生"""
        response = client.post('/doctor', json={
            'name': 'Dr. Test',
            'birth_date': '1980-01-01',
            'contact': '1234567890',
            'email': 'doctor@example.com',
            'department_id': 1,
            'specialization': 'Cardiology'
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_get_doctor_profile(self, client, auth_headers):
        """测试获取医生信息"""
        doctor_id = auth_headers.pop('doctor_id')
        if not doctor_id:
            pytest.skip("No doctor ID available")
        response = client.get(f'/doctor/profile/{doctor_id}', headers=auth_headers)
        print(f"Response: {response.data}")  # 添加调试信息
        assert response.status_code == 200

# 患者相关测试
class TestPatient:
    @pytest.fixture
    def auth_headers(self, client):
        """获取认证头"""
        response = client.post('/auth/login', json={
            'username': 'testpatient',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        # 获取患者ID
        patient = db.session.execute(text("""
            SELECT id FROM patients 
            WHERE user_id = (SELECT id FROM users WHERE username = 'testpatient')
        """)).fetchone()
        return {
            'Authorization': f'Bearer {token}',
            'patient_id': patient[0] if patient else None
        }

    def test_create_patient(self, client, auth_headers):
        """测试创建患者"""
        response = client.post('/patient', json={
            'name': 'Test Patient',
            'birth_date': '1990-01-01',
            'contact': '1234567890',
            'address': 'Test Address',
            'gender': 'M',
            'medical_history': 'None'
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_get_patient_profile(self, client, auth_headers):
        """测试获取患者信息"""
        patient_id = auth_headers.pop('patient_id')
        response = client.get(f'/patient/profile/{patient_id}', headers=auth_headers)
        assert response.status_code == 200

    def test_update_patient(self, client, auth_headers):
        """测试更新患者信息"""
        patient_id = auth_headers.pop('patient_id')
        response = client.put(f'/patient/{patient_id}', json={
            'contact': '9876543210',
            'address': 'New Address'
        }, headers=auth_headers)
        assert response.status_code == 200

# 护士相关测试
class TestNurse:
    @pytest.fixture
    def auth_headers(self, client):
        """获取认证头"""
        response = client.post('/auth/login', json={
            'username': 'testnurse',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        # 获取护士ID
        nurse = db.session.execute(text("""
            SELECT id FROM nurses 
            WHERE user_id = (SELECT id FROM users WHERE username = 'testnurse')
        """)).fetchone()
        return {
            'Authorization': f'Bearer {token}',
            'nurse_id': nurse[0] if nurse else None
        }

    def test_create_nurse(self, client, auth_headers):
        """测试创建护士"""
        response = client.post('/nurse', json={
            'name': 'Test Nurse',
            'birth_date': '1985-01-01',
            'contact': '1234567890',
            'email': 'nurse@example.com',
            'department_id': 1,
            'qualification': 'RN'
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_get_nurse_wards(self, client, auth_headers):
        """测试获取护士负责的病房"""
        nurse_id = auth_headers.pop('nurse_id')
        response = client.get(f'/nurse/{nurse_id}/wards', headers=auth_headers)
        assert response.status_code == 200

    def test_update_nurse_schedule(self, client, auth_headers):
        """测试更新护士排班"""
        response = client.put('/nurse/1/schedule', json={
            'ward_id': 1,
            'shift': 'morning'
        }, headers=auth_headers)
        assert response.status_code == 200

# 管理员相关测试
class TestAdmin:
    @pytest.fixture
    def auth_headers(self, client):
        """获取认证头"""
        response = client.post('/auth/login', json={
            'username': 'testadmin',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        return {'Authorization': f'Bearer {token}'}

    def test_create_department(self, client, auth_headers):
        """测试创建科室"""
        response = client.post('/admin/department', json={
            'name': 'New Department',
            'description': 'New department for testing'
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_create_ward(self, client, auth_headers):
        """测试创建病房"""
        response = client.post('/admin/ward', json={
            'room_number': 'B101',
            'ward_type': '特护病房',
            'bed_count': 2
        }, headers=auth_headers)
        assert response.status_code == 201

    def test_assign_nurse_to_ward(self, client, auth_headers):
        """测试分配护士到病房"""
        response = client.post('/admin/nurse-assignment', json={
            'nurse_id': 1,
            'ward_id': 1,
            'start_date': '2024-01-01'
        }, headers=auth_headers)
        assert response.status_code == 201

# 入院记录相关测试
class TestAdmission:
    @pytest.fixture
    def doctor_headers(self, client):
        """获取医生认证头"""
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        return {'Authorization': f'Bearer {token}'}

    def test_create_admission(self, client, doctor_headers):
        """测试创建入院记录"""
        response = client.post('/doctor/admission', json={
            'patient_id': 1,
            'ward_id': 1,
            'admission_date': '2024-01-01',
            'expected_discharge_date': '2024-01-10',
            'admission_reason': 'Test admission'
        }, headers=doctor_headers)
        assert response.status_code == 201

    def test_get_patient_admissions(self, client, doctor_headers):
        """测试获取患者入院记录"""
        response = client.get('/doctor/patient/1/admissions', headers=doctor_headers)
        assert response.status_code == 200

    def test_update_admission(self, client, doctor_headers):
        """测试更新入院记录"""
        response = client.put('/doctor/admission/1', json={
            'discharge_date': '2024-01-05',
            'discharge_notes': 'Early discharge'
        }, headers=doctor_headers)
        assert response.status_code == 200

# 治疗记录相关测试
class TestTreatment:
    @pytest.fixture
    def doctor_headers(self, client):
        """获取医生认证头"""
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        return {'Authorization': f'Bearer {token}'}

    def test_create_treatment(self, client, doctor_headers):
        """测试创建治疗记录"""
        response = client.post('/doctor/treatment', json={
            'patient_id': 1,
            'diagnosis': 'Test diagnosis',
            'treatment_plan': 'Test treatment plan',
            'medications': 'Test medications',
            'notes': 'Test notes'
        }, headers=doctor_headers)
        assert response.status_code == 201

    def test_get_patient_treatments(self, client, doctor_headers):
        """测试获取患者治疗记录"""
        response = client.get('/doctor/patient/1/treatments', headers=doctor_headers)
        assert response.status_code == 200

    def test_update_treatment(self, client, doctor_headers):
        """测试更新治疗记录"""
        response = client.put('/doctor/treatment/1', json={
            'treatment_outcome': 'Successful',
            'notes': 'Updated notes'
        }, headers=doctor_headers)
        assert response.status_code == 200

# 医患关系相关测试
class TestDoctorPatientRelation:
    @pytest.fixture
    def doctor_headers(self, client):
        """获取医生认证头"""
        response = client.post('/auth/login', json={
            'username': 'testdoctor',
            'password': 'password123'
        })
        token = json.loads(response.data)['token']
        return {'Authorization': f'Bearer {token}'}

    def test_create_patient_relation(self, client, doctor_headers):
        """测试创建医患关系"""
        response = client.post('/doctor/patient-relation', json={
            'patient_id': 1,
            'visit_date': '2024-01-01',
            'initial_diagnosis': 'Initial check'
        }, headers=doctor_headers)
        assert response.status_code == 201

    def test_get_doctor_patients(self, client, doctor_headers):
        """测试获取医生的患者列表"""
        response = client.get('/doctor/patients', headers=doctor_headers)
        assert response.status_code == 200

    def test_get_patient_doctors(self, client, doctor_headers):
        """测试获取患者主治医生列表"""
        response = client.get('/doctor/patient/1/doctors', headers=doctor_headers)
        assert response.status_code == 200
  