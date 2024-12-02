import os
import mysql.connector
from config import Config

def init_database():
    try:
        # 连接MySQL（不指定数据库）
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()

        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        cursor.execute(f"USE {Config.MYSQL_DB}")
        
        # 读取SQL文件
        sql_file_path = r"d:\微信文件\WeChat Files\wxid_adyzh55s3pk322\FileStorage\File\2024-11\dbms.sql"
        
        if not os.path.exists(sql_file_path):
            raise Exception(f"SQL file not found at {sql_file_path}")

        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()

        # 分割并执行SQL命令
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:  # 只执行非空命令
                try:
                    cursor.execute(command + ';')
                except mysql.connector.Error as err:
                    print(f"Error executing command: {err}")
                    print(f"Problematic command: {command}")
                    raise

        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise e
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    init_database() 