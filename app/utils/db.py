from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from sqlalchemy import text
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class Database:
    @classmethod
    def init_app(cls, app):
        """初始化数据库连接"""
        cls._configure_database(app)
        db.init_app(app)
        with app.app_context():
            cls._execute_sql_file('database/Hospital_Management_System.sql')

    @classmethod
    def _configure_database(cls, app):
        """配置数据库连接"""
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"postgresql+psycopg://"
            f"{app.config.get('DB_USER', 'postgres')}:"
            f"{app.config.get('DB_PASSWORD', '123456')}@"
            f"{app.config.get('DB_HOST', 'localhost')}:"
            f"{app.config.get('DB_PORT', '5432')}/"
            f"{app.config.get('DB_NAME', 'hospital_management_system')}"
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    @classmethod
    def _execute_sql_file(cls, file_path):
        """执行 SQL 文件中的所有命令"""
        with current_app.app_context():
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_commands = [cmd.strip() for cmd in f.read().split(';') if cmd.strip()]
            for command in sql_commands:
                try:
                    db.session.execute(text(command))
                except Exception as e:
                    db.session.rollback()
                    raise
            db.session.commit()

    @classmethod
    def execute(cls, query, params=None):
        """执行 SQL 查询并返回最后一个插入行的 ID"""
        return cls._execute_query(query, params, fetch_one=False)

    @classmethod
    def fetch_one(cls, query, params=None):
        """执行查询并返回单个结果"""
        result = cls._execute_query(query, params, fetch_one=True)
        return result

    @classmethod
    def fetch_all(cls, query, params=None):
        """执行查询并返回所有结果"""
        return cls._execute_query(query, params, fetch_one=False)

    @classmethod
    def _execute_query(cls, query, params=None, fetch_one=False):
        """执行查询并返回结果"""
        try:
            if isinstance(query, str):
                query = text(query)
            result = db.session.execute(query, params)
            db.session.commit()
            if fetch_one:
                return result.fetchone()
            return result.fetchall()
        except Exception as e:
            db.session.rollback()
            raise 