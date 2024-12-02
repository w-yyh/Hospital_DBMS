from app.utils.db_init import init_database
from app.utils.db_check import check_database_connection
from app import create_app

def init_project():
    try:
        # 初始化数据库
        print("Initializing database...")
        init_database()
        
        # 创建应用实例
        print("Creating Flask application...")
        app = create_app()
        
        # 检查数据库连接
        with app.app_context():
            if check_database_connection():
                print("Project initialized successfully!")
            else:
                print("Database check failed!")
                
    except Exception as e:
        print(f"Error during project initialization: {str(e)}")

if __name__ == '__main__':
    init_project() 