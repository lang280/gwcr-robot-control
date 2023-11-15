#!/bin/bash

# 获取脚本所在的目录
SCRIPT_DIR=$(dirname "$0")

# 安装pip
sudo apt-get upgrade -y
sudo apt-get install vim -y
sudo apt-get install python3-pip -y

# 安装包依赖
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# 检查PYTHONPATH
if ! grep -q 'export PYTHONPATH=\$PYTHONPATH:.:..' ~/.bashrc; then
  # 添加"."和".."到PYTHONPATH (方便包查找)
  echo "export PYTHONPATH=\$PYTHONPATH:.:.." >> ~/.bashrc
fi

# 赋予 run.sh 运行权限
chmod +x "$SCRIPT_DIR/run.sh"

# 允许端口绑定
sudo setcap 'cap_net_bind_service=+ep' $(readlink -f /usr/bin/python3)

# 安装视频录制工具ffmpeg
sudo apt install ffmpeg -y
