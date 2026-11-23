@echo off
chcp 65001
python editor.py
if %errorlevel% neq 0 (
    echo 启动失败！请确认已经安装Python，并且加入系统环境变量
    pause
)
