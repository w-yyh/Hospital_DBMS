from app import create_app
import socket
import random
import os
import sys

def get_free_port():
    """获取一个可用的端口号"""
    # 使用固定端口，方便调试
    return 5000
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.bind(('', 0))
    # port = sock.getsockname()[1]
    # sock.close()
    # return port

def get_ip_addresses():
    """获取本机所有IP地址"""
    hostname = socket.gethostname()
    addresses = []
    
    # 获取所有网卡的IP
    try:
        import netifaces
        for interface in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        addresses.append(addr['addr'])
            except:
                continue
    except ImportError:
        try:
            local_ip = socket.gethostbyname(hostname)
            addresses.append(local_ip)
        except:
            pass
    
    addresses.append('127.0.0.1')
    addresses.append('localhost')
    return list(set(addresses))  # 去重

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
    
    # 打印调试信息
    print("\n=== 调试信息 ===")
    print(f"模板目录: {app.template_folder}")
    print(f"静态文件目录: {app.static_folder}")
    print(f"已注册的蓝图: {list(app.blueprints.keys())}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print("\n=== 路由信息 ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
    
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 30 + "\n")
    
    try:
        # Windows开发环境配置
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
    except Exception as e:
        print(f"\n启动失败: {str(e)}")
        import traceback
        traceback.print_exc() 