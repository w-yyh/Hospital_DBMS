from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import psycopg
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class Database:
    @classmethod
    def init_app(cls, app):
        """初始化数据库连接"""
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"postgresql+psycopg://"
            f"{app.config.get('DB_USER', 'postgres')}:"
            f"{app.config.get('DB_PASSWORD', '123456')}@"
            f"{app.config.get('DB_HOST', 'localhost')}:"
            f"{app.config.get('DB_PORT', '5432')}/"
            f"{app.config.get('DB_NAME', 'hospital_management_system')}"
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # 读取并执行 SQL 文件
            with open('database/Hospital_Management_System.sql', 'r', encoding='utf-8') as f:
                sql = f.read()
                db.session.execute(text(sql))
                db.session.commit()
            
            # 插入测试用户
            test_users = [
                ('testadmin', 'password123', 'admin', 'admin@test.com'),
                ('testdoctor', 'password123', 'doctor', 'doctor@test.com'),
                ('testnurse', 'password123', 'nurse', 'nurse@test.com'),
                ('testpatient', 'password123', 'patient', 'patient@test.com')
            ]
            
            for username, password, role, email in test_users:
                # 检查用户是否已存在
                existing_user = db.session.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {'username': username}
                ).fetchone()
                
                if not existing_user:
                    # 生成新的密码哈希
                    password_hash = generate_password_hash(password)
                    
                    # 插入新用户
                    db.session.execute(text("""
                        INSERT INTO users (username, password_hash, role, email)
                        VALUES (:username, :password_hash, :role, :email)
                    """), {
                        'username': username,
                        'password_hash': password_hash,
                        'role': role,
                        'email': email
                    })
            
            db.session.commit()
        
        return cls

    @classmethod
    def execute(cls, query, params=None):
        """执行SQL查询并返回最后一个插入行的ID"""
        try:
            if isinstance(query, str):
                query = text(query)
            result = db.session.execute(query, params)
            db.session.commit()
            if result.returns_rows:
                row = result.fetchone()
                return row[0] if row else None
            return None
        except Exception as e:
            db.session.rollback()
            raise

    @classmethod
    def fetch_one(cls, query, params=None):
        """执行查询并返回单个结果"""
        try:
            if isinstance(query, str):
                query = text(query)
            result = db.session.execute(query, params)
            row = result.fetchone()
            if not row:
                return None
            return {key: value for key, value in zip(result.keys(), row)}
        except Exception as e:
            db.session.rollback()
            raise

    @classmethod
    def fetch_all(cls, query, params=None):
        """执行查询并返回所有结果"""
        try:
            if isinstance(query, str):
                query = text(query)
            result = db.session.execute(query, params)
            return [{key: value for key, value in zip(result.keys(), row)} for row in result]
        except Exception as e:
            db.session.rollback()
            raise

    @classmethod
    def execute_query(cls, query, params=None):
        """执行查询但不返回结果"""
        try:
            if isinstance(query, str):
                query = text(query)
            db.session.execute(query, params)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise 