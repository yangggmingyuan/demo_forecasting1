# -*- coding: utf-8 -*-
"""启动 Streamlit 应用"""
import os
import subprocess
import sys
import webbrowser
import time
import threading

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 在后台线程中打开浏览器
def open_browser():
    time.sleep(3)  # 等待 Streamlit 启动
    webbrowser.open('http://localhost:8501')

# 启动浏览器线程
browser_thread = threading.Thread(target=open_browser, daemon=True)
browser_thread.start()

# 运行 streamlit
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "false"])

