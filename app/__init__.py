from flask import Flask
from flask_cors import CORS
from app.utils.db import Database, db
import os

def create_app(config_name='development'):
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # 启用 CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # 在生产环境中应该限制具体的域名
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 添加 SECRET_KEY 配置
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # 数据库配置
    app.config.update(
        DB_NAME='hospital_management_system',
        DB_USER='postgres',
        DB_PASSWORD='123456',
        DB_HOST='localhost',
        DB_PORT='5432'
    )
    
    # 初始化数据库
    Database.init_app(app)
    
    # 创建所有数据库表
    with app.app_context():
        db.create_all()
    
    # 注册蓝图
    from app.routes import admin, auth, doctor, nurse, patient
    from app import front
    
    app.register_blueprint(admin.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(nurse.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(front.bp)
    
    return app 