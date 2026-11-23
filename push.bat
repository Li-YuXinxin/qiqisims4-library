@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Sims4 资源库 · 一键提交并部署到 Cloudflare
echo ============================================

git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo [错误] 当前文件夹还不是 git 仓库。
    echo 请先在仓库地址里点「Code」复制 HTTPS 地址，然后执行：
    echo   git init
    echo   git remote add origin 你的仓库地址
    pause
    exit /b 1
)

git add .
git diff --cached --quiet
if not errorlevel 1 (
    echo [提示] 没有检测到任何改动，无需提交。
    pause
    exit /b 0
)

git commit -m "update data %date% %time%"
if errorlevel 1 (
    echo [错误] 提交失败，请检查上面的报错信息。
    pause
    exit /b 1
)

git push
if errorlevel 1 (
    echo.
    echo [错误] 推送失败。常见原因：
    echo   1. 网络问题，重试一次；
    echo   2. 需要 GitHub Token 而不是密码。
    pause
    exit /b 1
)

echo.
echo [完成] 已推送到 GitHub。
echo Cloudflare Pages 会在约 30 秒后自动重新部署，刷新网站即可看到更新。
echo.
pause
