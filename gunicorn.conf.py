# Gunicorn 配置文件
bind = "0.0.0.0:5000"  # 监听所有网络接口的5000端口
workers = 4  # 工作进程数
worker_class = "sync"  # 工作进程类型
timeout = 120  # 超时时间
keepalive = 5  # keep-alive 连接超时时间

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info" 