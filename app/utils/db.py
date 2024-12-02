from flask import current_app, jsonify
from flask_mysqldb import MySQL

class Database:
    @staticmethod
    def get_mysql():
        """获取MySQL连接"""
        if 'mysql' not in current_app.extensions:
            raise Exception("MySQL extension not initialized")
        return current_app.extensions['mysql']

    @staticmethod
    def execute_query(query, args=None):
        mysql = Database.get_mysql()
        cur = mysql.connection.cursor()
        try:
            cur.execute(query, args or ())
            mysql.connection.commit()
            return cur
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cur.close()

    @staticmethod
    def fetch_one(query, args=None):
        mysql = Database.get_mysql()
        cur = mysql.connection.cursor()
        try:
            cur.execute(query, args or ())
            result = cur.fetchone()
            if result:
                # 将结果转换为字典
                columns = [col[0] for col in cur.description]
                return dict(zip(columns, result))
            return None
        finally:
            cur.close()

    @staticmethod
    def fetch_all(query, args=None):
        mysql = Database.get_mysql()
        cur = mysql.connection.cursor()
        try:
            cur.execute(query, args or ())
            results = cur.fetchall()
            # 将结果转换为字典列表
            columns = [col[0] for col in cur.description]
            return [dict(zip(columns, row)) for row in results]
        finally:
            cur.close() 