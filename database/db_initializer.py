import os
import mysql.connector
from getpass import getpass
import sys
import re

class DatabaseInitializer:
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.db_name = 'Hospital_Management_System'
        self.sql_file = os.path.join(os.path.dirname(__file__), 'Hospital_Management_System.sql')

    def get_credentials(self):
        """获取数据库凭据"""
        print("\n=== MySQL数据库初始化工具 ===")
        print(f"默认主机: {self.host}")
        print(f"默认用户: {self.user}")
        print(f"默认数据库名: {self.db_name}\n")

        use_default = input("是否使用默认设置? (y/n): ").lower() == 'y'
        
        if not use_default:
            self.host = input(f"主机 ({self.host}): ") or self.host
            self.user = input(f"用户名 ({self.user}): ") or self.user
            self.db_name = input(f"数据库名 ({self.db_name}): ") or self.db_name

        password = getpass("请输入MySQL密码: ")
        return password

    def parse_sql_file(self, sql_content):
        """解析SQL文件，处理DELIMITER语句"""
        # 用于存储解析后的SQL命令
        commands = []
        # 当前的分隔符
        current_delimiter = ';'
        # 用于存储多行命令
        current_command = ''
        
        # 按行处理SQL文件
        for line in sql_content.splitlines():
            # 去除首尾空白
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith('--') or line.startswith('/*'):
                continue
                
            # 检查是否是DELIMITER语句
            delimiter_match = re.match(r'DELIMITER\s+(\S+)', line, re.I)
            if delimiter_match:
                # 如果当前有未完成的命令，先添加到列表中
                if current_command:
                    commands.append(current_command)
                    current_command = ''
                # 更新分隔符
                current_delimiter = delimiter_match.group(1)
                continue
                
            # 检查行是否以当前分隔符结束
            if line.endswith(current_delimiter):
                # 移除行尾的分隔符
                line = line[:-len(current_delimiter)]
                current_command += line + '\n'
                # 添加完整的命令到列表中
                if current_command:
                    commands.append(current_command.strip())
                    current_command = ''
            else:
                current_command += line + '\n'
                
        # 添加最后一个命令（如果有的话）
        if current_command:
            commands.append(current_command.strip())
            
        return commands

    def initialize_database(self):
        """初始化数据库"""
        try:
            # 获取用户输入
            password = self.get_credentials()

            # 检查SQL文件是否存在
            if not os.path.exists(self.sql_file):
                raise Exception(f"SQL文件未找到: {self.sql_file}")

            # 连接MySQL（不指定数据库）
            print("\n正在连接MySQL服务器...")
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=password
            )
            cursor = conn.cursor()

            # 创建数据库
            print(f"正在创建数据库 {self.db_name}...")
            cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
            cursor.execute(f"CREATE DATABASE {self.db_name}")
            cursor.execute(f"USE {self.db_name}")

            # 读取SQL文件
            print("正在导入数据库结构和数据...")
            with open(self.sql_file, 'r', encoding='utf-8') as file:
                sql_content = file.read()

            # 解析SQL命令
            commands = self.parse_sql_file(sql_content)

            # 执行SQL命令
            for command in commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                        conn.commit()  # 每个命令后都提交
                    except mysql.connector.Error as err:
                        print(f"\n错误执行命令: {err}")
                        print(f"问题命令: {command[:200]}...")  # 显示更多内容以便调试
                        raise

            # 验证数据库结构
            print("\n正在验证数据库结构...")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"成功创建的表: {', '.join([table[0] for table in tables])}")

            # 验证触发器
            cursor.execute("SHOW TRIGGERS")
            triggers = cursor.fetchall()
            print(f"成功创建的触发器: {', '.join([trigger[0] for trigger in triggers])}")

            # 生成配置文件
            self._generate_config(password)

            print("\n=== 数据库初始化成功! ===")
            print(f"数据库名称: {self.db_name}")
            print(f"配置文件已更新: config.py")
            
        except Exception as e:
            print(f"\n错误: {str(e)}")
            sys.exit(1)
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def _generate_config(self, password):
        """生成配置文件"""
        config_template = f'''class Config:
    SECRET_KEY = 'hospital-management-2024'
    MYSQL_HOST = '{self.host}'
    MYSQL_USER = '{self.user}'
    MYSQL_PASSWORD = '{password}'
    MYSQL_DB = '{self.db_name}'
    MYSQL_CURSORCLASS = 'DictCursor'
'''
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_template)

if __name__ == '__main__':
    initializer = DatabaseInitializer()
    initializer.initialize_database() 