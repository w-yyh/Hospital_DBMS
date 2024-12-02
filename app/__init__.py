from flask import Flask
from flask_mysqldb import MySQL

# 首先创建mysql实例
mysql = MySQL()

def create_app():
    app = Flask(__name__)
    
    # 配置数据库
    app.config.from_object('config.Config')
    
    # 初始化mysql并确保它被正确注册到app.extensions
    mysql.init_app(app)
    app.extensions['mysql'] = mysql
    
    # 导入并注册所有蓝图
    from app.routes import auth, admin, doctor, patient
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(patient.bp)
    
    return app 