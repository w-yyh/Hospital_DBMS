from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import psycopg
from sqlalchemy import text

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
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'client_encoding': 'utf8',
            'connect_args': {
                'client_encoding': 'UTF8'
            }
        }
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            
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