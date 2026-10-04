@echo off
REM ============================================================
REM  多平台内容下载器 - PyInstaller 打包脚本
REM ============================================================
REM  用法:
REM    1. 确保已激活虚拟环境 (.venv)
REM    2. 双击本文件，或在命令行执行: build.bat
REM ============================================================

echo [1/3] 清理旧产物...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "multi-platform-downloader.spec" del /q "multi-platform-downloader.spec"

echo [2/3] 开始打包 (预计 5-10 分钟)...
pyinstaller --onefile --windowed ^
  --name "multi-platform-downloader" ^
  --add-data "bin/ffmpeg.exe;bin" ^
  --add-data "third_party/douyin-downloader-skill;douyin_dl" ^
  --add-data "third_party/fanqiexiaoshuo-Download;fanqie_dl" ^
  --add-data "third_party/KS-Downloader;KS-Downloader" ^
  --collect-all yt_dlp ^
  --collect-all bilibili_api ^
  --collect-all aiohttp ^
  --collect-all httpx ^
  --collect-all curl_cffi ^
  --collect-all fastapi ^
  --collect-all uvicorn ^
  --collect-all rich ^
  --collect-all aiosqlite ^
  --collect-all fontTools ^
  --collect-all brotli ^
  --hidden-import PySide6.QtSvg ^
  --hidden-import PySide6.QtNetwork ^
  --hidden-import yaml ^
  --hidden-import qrcode ^
  --hidden-import PIL ^
  --hidden-import PIL.Image ^
  --hidden-import flask ^
  --hidden-import jinja2 ^
  --hidden-import ebooklib ^
  --hidden-import lxml ^
  --hidden-import lxml.etree ^
  --hidden-import bs4 ^
  --hidden-import tqdm ^
  --clean --noconfirm ^
  multi_dl.py

if errorlevel 1 (
    echo.
    echo [ERROR] 打包失败，请查看上面的输出。
    pause
    exit /b 1
)

echo [3/3] 打包完成！
echo.
echo 产物位置: dist\multi-platform-downloader.exe
dir "dist\multi-platform-downloader.exe" | findstr "multi-platform-downloader.exe"
echo.
echo 测试方法:
echo   在命令行里执行 dist\multi-platform-downloader.exe
echo   (不要直接双击，否则报错信息会一闪而过)
pause