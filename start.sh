#!/bin/bash
# 创建日志目录
mkdir -p logs

# 使用 gunicorn 启动应用
gunicorn -c gunicorn.conf.py "app:create_app()" 