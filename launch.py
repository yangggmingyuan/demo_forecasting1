#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
from pathlib import Path

# 获取脚本所在目录
script_dir = Path(__file__).parent.absolute()
app_file = script_dir / "app.py"

print(f"脚本目录: {script_dir}")
print(f"应用文件: {app_file}")
print(f"文件存在: {app_file.exists()}")

if app_file.exists():
    # 切换到脚本目录
    import os
    os.chdir(str(script_dir))
    print(f"当前工作目录: {os.getcwd()}")
    
    # 运行 streamlit
    subprocess.run([
        sys.executable, 
        "-m", "streamlit", 
        "run", 
        str(app_file.name),
        "--server.headless", "false"
    ])
else:
    print(f"错误: 找不到文件 {app_file}")

