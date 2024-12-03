import sys
import os
import asyncio
import asyncpg
import psycopg
from urllib.parse import quote_plus

async def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        print("\n尝试创建数据库")
        # 连接到默认的 postgres 数据库
        conn = psycopg.connect(
            dbname='postgres',
            user='postgres',
            password='123456',
            host='localhost',
            port='5432',
            autocommit=True
        )
        
        # 检查数据库是否存在
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 1 FROM pg_database 
                WHERE datname = 'hospital_management_system'
            """)
            exists = cur.fetchone() is not None
            
            if not exists:
                print("数据库不存在，正在创建...")
                # 创建数据库
                cur.execute("""
                    CREATE DATABASE hospital_management_system
                    WITH ENCODING = 'UTF8'
                    LC_COLLATE = 'Chinese (Simplified)_China.936'
                    LC_CTYPE = 'Chinese (Simplified)_China.936'
                    TEMPLATE template0;
                """)
                print("数据库创建成功！")
            else:
                print("数据库已存在")
        
        conn.close()
        return True
    except Exception as e:
        print(f"创建数据库失败: {str(e)}")
        return False

def test_psycopg3_connection():
    """使用 psycopg3 测试连接"""
    try:
        print("\n尝试 psycopg3 连接")
        conn = psycopg.connect(
            dbname='hospital_management_system',
            user='postgres',
            password='123456',
            host='localhost',
            port='5432',
            autocommit=True
        )
        
        # 测试连接
        with conn.cursor() as cur:
            cur.execute('SELECT version()')
            version = cur.fetchone()[0]
            print(f"连接成功！PostgreSQL 版本: {version}")
            
            cur.execute('SHOW client_encoding')
            encoding = cur.fetchone()[0]
            print(f"客户端编码: {encoding}")
            
            # 检查所有编码设置
            cur.execute('SHOW server_encoding')
            server_encoding = cur.fetchone()[0]
            print(f"服务器编码: {server_encoding}")
            
            cur.execute('SHOW lc_collate')
            lc_collate = cur.fetchone()[0]
            print(f"排序规则: {lc_collate}")
            
            cur.execute('SHOW lc_ctype')
            lc_ctype = cur.fetchone()[0]
            print(f"字符类型: {lc_ctype}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"psycopg3 连接失败: {str(e)}")
        return False

async def test_asyncpg_connection():
    """使用 asyncpg 测试连接"""
    try:
        print("\n尝试 asyncpg 连接")
        conn = await asyncpg.connect(
            user='postgres',
            password='123456',
            database='hospital_management_system',
            host='localhost'
        )
        
        # 测试连接
        version = await conn.fetchval('SELECT version()')
        print(f"连接成功！PostgreSQL 版本: {version}")
        
        # 检查编码
        encoding = await conn.fetchval('SHOW client_encoding')
        print(f"客户端编码: {encoding}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"asyncpg 连接失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("\n=== 系统环境检查 ===")
    print(f"Python 版本: {sys.version}")
    print(f"默认编码: {sys.getdefaultencoding()}")
    print(f"文件系统编码: {sys.getfilesystemencoding()}")
    
    # 设置环境变量
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    os.environ['LANG'] = 'C'
    os.environ['LC_ALL'] = 'C'
    
    print("\n=== 数据库测试 ===")
    
    # 创建数据库
    if await create_database_if_not_exists():
        # 测试连接
        psycopg3_success = test_psycopg3_connection()
        asyncpg_success = await test_asyncpg_connection()
        
        if psycopg3_success or asyncpg_success:
            print("\n数据库连接测试成功！")
        else:
            print("\n所有连接方式都失败！")

if __name__ == "__main__":
    asyncio.run(main()) 