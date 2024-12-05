import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    # 数据库连接参数
    DB_NAME = 'hospital_management_system'
    DB_USER = 'postgres'
    DB_PASSWORD = '123456'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    
    try:
        # 首先连接到默认的 postgres 数据库
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # 删除已存在的数据库（如果存在）
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        print(f"Dropped existing database {DB_NAME}")
        
        # 创建新数据库
        cur.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Created new database {DB_NAME}")
        
        # 关闭到 postgres 的连接
        cur.close()
        conn.close()
        
        # 连接到新创建的数据库
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        # 读取并执行 SQL 文件
        with open('database/Hospital_Management_System.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read()
            cur.execute(sql_commands)
        
        conn.commit()
        print("Successfully initialized database schema")
        
        # 关闭连接
        cur.close()
        conn.close()
        
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 