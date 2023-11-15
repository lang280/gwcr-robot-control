"""
作用: GPIO控制驱动
作者: Jianjun Lang
日期: 2024/10/30
版本: v1.0
更多描述:
    合并所有GPIO驱动
    每个GPIO组件使用单独的线程, 单独的port接收命令
"""

import socket
import threading
import struct
import RPi.GPIO
    
# handle GPIO commands
def udpServer(driverPort, PWMobjects, driverPort_tuple, pin_tuple, gpioDriver_logPrint):
    # 创建一个UDP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定到指定的端口
    server_socket.bind(("0.0.0.0", driverPort))

    # 根据不同的端口(部件), 使用不同的处理逻辑
    if driverPort == driverPort_tuple[0]:
        # 左驱动马达
        while True:
            # 接收命令, 提取速度
            data, addr = server_socket.recvfrom(256)
            motorSpeed = struct.unpack('!i', data)[0]
            
            # 设置马达方向
            motorDirection = RPi.GPIO.HIGH if motorSpeed < 0 else RPi.GPIO.LOW
            RPi.GPIO.output(pin_tuple[-1], motorDirection)
            # 设置马达转速
            PWMobjects[0].ChangeDutyCycle(abs(motorSpeed))

            # 打印速度
            if gpioDriver_logPrint > 1:
                print("LeftMotor:", motorSpeed)
        

    elif driverPort == driverPort_tuple[1]:
        # 右驱动马达
        while True:
            # 接收命令, 提取速度
            data, addr = server_socket.recvfrom(256)
            motorSpeed = struct.unpack('!i', data)[0]
            
            # 设置马达方向
            motorDirection = RPi.GPIO.LOW if motorSpeed < 0 else RPi.GPIO.HIGH
            RPi.GPIO.output(pin_tuple[-2], motorDirection)
            # 设置马达转速
            PWMobjects[1].ChangeDutyCycle(abs(motorSpeed))

            # 打印速度
            if gpioDriver_logPrint > 1:
                print("RightMotor:", motorSpeed)
        

    elif driverPort == driverPort_tuple[2]:
        # 吸墙马达
        while True:
            # 接收命令
            data, addr = server_socket.recvfrom(256)
            motorSpeed = struct.unpack('!i', data)[0]
            
            # 设置马达转速
            PWMobjects[2].ChangeDutyCycle(motorSpeed)

            # 打印速度
            if gpioDriver_logPrint > 1:
                print("SuctionMotor:", motorSpeed)
        

    elif driverPort == driverPort_tuple[3]:
        # 状态指示灯
        while True:
            # 接收命令
            data, addr = server_socket.recvfrom(256)
            # 设置LED电平
            RPi.GPIO.output(pin_tuple[3], struct.unpack('!i', data)[0])
        

    else:
        # 其它情况
        print("正在设置未知端口")
        while True:
            # 接收命令, 提取速度
            data, addr = server_socket.recvfrom(256)
            # 打印接收到的数据和发送方的地址
            print(f"端口{driverPort}从{addr}接收信息: {data}")


def run_gpio_driver(driverPort_tuple, pin_tuple, pwmFreq_tuple, gpioDriver_logPrint):
    # GPIO警报关闭
    RPi.GPIO.setwarnings(False)

    # overwrite previous GPIO settings
    RPi.GPIO.setmode(RPi.GPIO.BCM)
    for pin in list(range(2, 28)):
        RPi.GPIO.setup(pin, RPi.GPIO.IN)
    RPi.GPIO.cleanup()

    # set pin to BCM
    RPi.GPIO.setmode(RPi.GPIO.BCM)

    # set pin to output
    for pin in pin_tuple:
        RPi.GPIO.setup(pin, RPi.GPIO.OUT)

    # 创建PWM object
    PWMobjects = []
    PWMobjects.append(RPi.GPIO.PWM(pin_tuple[0], pwmFreq_tuple[0]))
    PWMobjects.append(RPi.GPIO.PWM(pin_tuple[1], pwmFreq_tuple[0]))
    PWMobjects.append(RPi.GPIO.PWM(pin_tuple[2], pwmFreq_tuple[1]))

    # 启动 PWM 信号输出, 初始化空占比0
    for PWMobject in PWMobjects:
        PWMobject.start(0)

    # 创建一个线程列表
    threads = []

    # 启动线程
    for driverPort in driverPort_tuple:
        # creat thread
        thread = threading.Thread(target=udpServer, args=(driverPort, PWMobjects, driverPort_tuple, pin_tuple, gpioDriver_logPrint))
        # 启动线程
        thread.start()
        # 将线程添加到线程列表
        threads.append(thread)

    # 等待所有线程结束
    for thread in threads:
        thread.join()
    
    print("gpio driver ended")
