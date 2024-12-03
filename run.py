from app import create_app
import socket
import random

def get_free_port():
    """获取一个可用的端口号"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def get_ip_addresses():
    """获取本机所有IP地址"""
    hostname = socket.gethostname()
    addresses = []
    try:
        # 获取本机IP
        local_ip = socket.gethostbyname(hostname)
        addresses.append(local_ip)
    except:
        pass
    
    # 添加 localhost
    addresses.append('127.0.0.1')
    addresses.append('localhost')
    return addresses

app = create_app()

if __name__ == '__main__':
    # 获取可用端口
    port = get_free_port()
    
    # 获取IP地址
    ip_addresses = get_ip_addresses()
    
    print("\n=== 服务器启动成功 ===")
    print("\n可通过以下地址访问：")
    for ip in ip_addresses:
        print(f"http://{ip}:{port}")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 30 + "\n")
    
    # Windows开发环境配置
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=port,       # 使用自动分配的端口
        debug=True       # 开发环境可以启用debug模式
    ) 