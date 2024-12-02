import unittest
import sys
import os
import mysql.connector
from flask import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config import Config
from database.db_initializer import DatabaseInitializer
from app.utils.db import Database

class HospitalSystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        - 初始化数据库
        - 创建Flask测试客户端
        """
        # 初始化数据库
        cls.initializer = DatabaseInitializer()
        try:
            cls.initializer.initialize_database()
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            sys.exit(1)

        # 创建测试应用
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    def setUp(self):
        """每个测试用例开始前执行"""
        # 添加测试用户数据
        try:
            # 添加测试医生
            Database.execute_query("""
                INSERT INTO doctors (doctor_id, name, email, specialization, department_id, 
                                   dob, contact_number)
                VALUES (999, 'Test Doctor', 'test@test.com', 'Testing', 1,
                       '1990-01-01', '13800138000')
                ON DUPLICATE KEY UPDATE 
                    name = 'Test Doctor',
                    email = 'test@test.com'
            """)
            
            # 添加测试病人
            Database.execute_query("""
                INSERT INTO patients (patient_id, name, contact_number, dob, gender)
                VALUES (999, 'Test Patient', 'test@test.com', '1990-01-01', 'M')
                ON DUPLICATE KEY UPDATE 
                    name = 'Test Patient',
                    contact_number = 'test@test.com'
            """)
            
        except Exception as e:
            print(f"Error setting up test data: {e}")

    def tearDown(self):
        """每个测试用例结束后执行"""
        try:
            # 清理测试数据
            Database.execute_query("DELETE FROM doctors WHERE doctor_id = 999")
            Database.execute_query("DELETE FROM patients WHERE patient_id = 999")
        except Exception as e:
            print(f"Error cleaning up test data: {e}")

    @classmethod
    def tearDownClass(cls):
        """测试类结束后执行"""
        cls.app_context.pop()

    def test_database_connection(self):
        """测试数据库连接"""
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB
            )
            self.assertTrue(conn.is_connected())
            conn.close()
        except Exception as e:
            self.fail(f"数据库连接失败: {str(e)}")

    def test_database_tables(self):
        """测试数据库表结构"""
        expected_tables = {
            'departments': ['department_id', 'department_name'],
            'doctors': ['doctor_id', 'name', 'specialization'],
            'nurses': ['nurse_id', 'name'],
            'patients': ['patient_id', 'name'],
            'patient_doctor': ['patient_id', 'doctor_id'],
            'patient_room': ['patient_id', 'room_id'],
            'rooms': ['room_id', 'room_type']
        }

        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()

        # 检查每个表的存在性和结构
        for table, expected_columns in expected_tables.items():
            # 检查表是否存在
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            self.assertTrue(cursor.fetchone(), f"表 {table} 不存在")

            # 检查表结构
            cursor.execute(f"DESCRIBE {table}")
            columns = [row[0] for row in cursor.fetchall()]
            for column in expected_columns:
                self.assertIn(column, columns, f"表 {table} 缺少列 {column}")

        cursor.close()
        conn.close()

    def test_triggers(self):
        """测试触发器是否存在且正常工作"""
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()

        # 检查触发器是否存在
        cursor.execute("SHOW TRIGGERS")
        triggers = [trigger[0] for trigger in cursor.fetchall()]
        expected_triggers = ['SyncAdmissionDate', 'SyncDischargeDate']
        for trigger in expected_triggers:
            self.assertIn(trigger, triggers, f"触发器 {trigger} 不存在")

        cursor.close()
        conn.close()

    def get_auth_token(self, user_type='admin'):
        """获取认证token的辅助方法"""
        login_data = {
            'user_type': user_type,
            'email': 'test@test.com',
            'password': 'password'
        }
        
        # 确保测试数据存在
        self.setUp()  # 添加测试数据
        
        response = self.client.post('/login', json=login_data)
        
        if response.status_code != 200:
            print(f"Login failed with status {response.status_code}")
            print(f"Response: {response.data.decode()}")
            raise Exception("Login failed")
        
        data = json.loads(response.data)
        if 'token' not in data:
            print(f"No token in response: {data}")
            raise Exception("No token in response")
        
        return data['token']

    def test_admin_endpoints(self):
        """测试管理员API端点"""
        # 获取认证token
        token = self.get_auth_token('admin')
        headers = {'Authorization': f'Bearer {token}'}

        # 测试获取所有医生
        response = self.client.get('/admin/doctors', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

        # 测试添加新医生
        new_doctor = {
            'doctor_id': 1000,
            'name': 'Dr. Test',
            'dob': '1990-01-01',
            'contact_number': '13800138000',
            'specialization': 'Testing',
            'department_id': 1,
            'email': 'test_new@test.com'
        }
        response = self.client.post('/admin/doctor',
                                  json=new_doctor,
                                  headers=headers,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_doctor_endpoints(self):
        """测试医生API端点"""
        # 获取认证token
        token = self.get_auth_token('doctor')
        headers = {'Authorization': f'Bearer {token}'}

        # 测试获取医生的病人列表
        response = self.client.get('/doctor/patients', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 测试更新诊断（使用测试医生ID 999）
        update_data = {
            'patient_id': 999,
            'diagnosis': 'Test diagnosis'
        }
        response = self.client.post('/doctor/update-diagnosis',
                                  json=update_data,
                                  headers=headers,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_patient_endpoints(self):
        """测试病人API端点"""
        # 获取认证token
        token = self.get_auth_token('patient')
        headers = {'Authorization': f'Bearer {token}'}

        # 测试获取病人信息（使用测试用户ID 999）
        response = self.client.get('/patient/profile/999', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 测试获取病人的医生列表
        response = self.client.get('/patient/doctors/999', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_data_integrity(self):
        """测试数据完整性"""
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor(dictionary=True)

        # 测试外键约束
        cursor.execute("SELECT * FROM patient_doctor")
        for record in cursor.fetchall():
            # 验证病人ID存在
            cursor.execute(f"SELECT * FROM patients WHERE patient_id = {record['patient_id']}")
            self.assertIsNotNone(cursor.fetchone(), f"病人ID {record['patient_id']} 不存在")
            
            # 验证医生ID存在
            cursor.execute(f"SELECT * FROM doctors WHERE doctor_id = {record['doctor_id']}")
            self.assertIsNotNone(cursor.fetchone(), f"医生ID {record['doctor_id']} 不存在")

        cursor.close()
        conn.close()

def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    run_tests() 