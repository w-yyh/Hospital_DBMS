from app import mysql
from flask import jsonify

def check_database_connection():
    """仅用于运行时检查数据库连接状态"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False 