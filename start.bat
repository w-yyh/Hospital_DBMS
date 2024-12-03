@echo off
:: 创建日志目录
if not exist logs mkdir logs

:: 使用 gunicorn 启动应用
python -m gunicorn -c gunicorn.conf.py "app:create_app()" 