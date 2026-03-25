@echo off
chcp 65001 >nul
:: 修复跨盘符跳转问题，强制锁定当前文件夹
cd /d "%~dp0"

echo ==========================================
echo   📊 开始打包 OmniChart (万象数图)
echo ==========================================

:: 1. 自动激活虚拟环境（极其关键！）
if exist ".venv\Scripts\activate.bat" (
    echo [1/4] 检测到虚拟环境 .venv，正在自动激活...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] 未检测到虚拟环境，将尝试使用全局环境...
)

:: 2. 智能寻找 Python 源码文件
set "TARGET_PY="
if exist "main.py" (
    set "TARGET_PY=main.py"
) else if exist "time_pie_chart.py" (
    set "TARGET_PY=time_pie_chart.py"
) else (
    echo.
    echo ❌ 致命错误：找不到 Python 源码文件！
    echo 请确保您的代码文件名为 main.py 或 time_pie_chart.py，并且和 build.bat 放在同一个文件夹下。
    echo ==========================================
    pause
    exit /b
)
echo [2/4] 成功锁定源码文件: %TARGET_PY%

echo [3/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OmniChart.spec del /q OmniChart.spec

echo [4/4] 正在执行打包核心程序 (这可能需要几分钟，请耐心等待)...
:: 使用更稳定的 python -m 模块调用方式
python -m PyInstaller -w -F --collect-all customtkinter --add-data "app_icon.ico;." -i app_icon.ico --name "OmniChart" "%TARGET_PY%"

echo.
echo ==========================================
echo 🎉 打包流程结束！
echo 如果上方没有出现红色的 Error 报错，您的软件已经生成。
echo 请前往当前目录下的 dist 文件夹查看 OmniChart.exe
echo ==========================================
pause