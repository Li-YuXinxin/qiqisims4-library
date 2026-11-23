@echo off
chcp 65001
echo 启动本地预览服务器，端口8000
start http://localhost:8000
python -m http.server 8000
pause
