# EN
## GWCR Robot Control Program
### Functionality:
Control the robot to move forward, backward, turn left, turn right, and control suction power based on web page commands. Provides real-time video based on PiCamera.

### Requirements:
Support for Raspberry Pi GPIO.
Raspberry Pi PiCamera.
Note: The main control part, web interaction, and signal transmission are universally applicable across Python platforms. Only the hardware driver content (under the 'drivers' directory) is specific to Raspberry Pi.

### Installation:
Run 'setup.sh' using Bash.

### Operation:
Run 'run.sh' using Bash, or directly execute 'python3 -m code.main'.
Open the robot control web page (according to the robot's IP address on the LAN) to operate.


# 中文
## GWCR机器人控制程序
### 功能:
基于网页控制机器人前进后退, 左转右转, 吸力, 提供基于picamera的实时视频

### 需求:
树莓派GPIO支持
树莓派picamera
注: 主体控制部分, 网页交互, 信号传递都基于python全平台通用, 仅硬件驱动部分(drivers 目录下的内容)限制于树莓派

### 安装:
使用bash运行setup.sh

### 运行:
使用bash运行run.sh, 或直接运行python3 -m code.main
打开机器人控制网页(根据机器人在LAN上的ip地址)进行操作
