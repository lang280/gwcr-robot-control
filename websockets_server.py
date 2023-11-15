"""
作用:
    接受client websocket的连接,
    提取速度转向吸力数据
    将这些数据通过udp发送到马达驱动
作者: Jianjun Lang
日期: 2024/10/10
版本: v1.0
更多描述:

"""

import socket
import struct
import sys
import asyncio
import websockets


'''
函数定义
'''
# 导入参数

# websocket服务器端
class WebSocketHandler:
    udpSocket = None
    leftMotor_port = None
    rightMotor_port = None
    suctionMotor_port = None
    websocket_logPrint = None

    def __init__(self):
        self.speed_num = 0
        self.steering_num = 0
        self.suction_num = 0
    
    # 发送udp(马达速度, 发送端口, 接受IP, 接收端口)
    def udp_send_number(number, dest_ip, dest_port):
        # 使用struct打包数字为二进制数据
        data = struct.pack('!i', number)

        # 发送打包后的数据
        WebSocketHandler.udpSocket.sendto(data, (dest_ip, dest_port))

    async def connection_handling(self, websocket, path):
        # 显示连接的远程客户端的IP地址和端口
        if WebSocketHandler.websocket_logPrint > 1:
            print(f"websocket ---> {websocket.remote_address[0]}:{websocket.remote_address[1]}")

        try:
            async for message in websocket:
                if WebSocketHandler.websocket_logPrint > 1:
                    print(f"websocket message: {message}")
                
                # 处理message
                # 提取控制参数
                message_parts = message.split('|')
                

                # 判断速度是否需要更新
                if message_parts[0] != '-':
                    new_speed_num = int(message_parts[0])
                    # 更新存储
                    self.speed_num = new_speed_num
                    # 计算机器人左右马达速度
                    motor_speed_left = new_speed_num * 20 + self.steering_num * 20
                    motor_speed_right = new_speed_num * 20 - self.steering_num * 20
                    # 发送速度到马达驱动
                    WebSocketHandler.udp_send_number(motor_speed_left, 'localhost', WebSocketHandler.leftMotor_port)
                    WebSocketHandler.udp_send_number(motor_speed_right, 'localhost', WebSocketHandler.rightMotor_port)
                
                # 判断转向是否需要更新
                if message_parts[1] != '-':
                    new_steering_num = int(message_parts[1])
                    # 更新存储
                    self.steering_num = new_steering_num
                    # 计算机器人左右马达速度
                    motor_speed_left = self.speed_num * 20 + new_steering_num * 20
                    motor_speed_right = self.speed_num * 20 - new_steering_num * 20
                    # 发送速度到马达驱动
                    WebSocketHandler.udp_send_number(motor_speed_left, 'localhost', WebSocketHandler.leftMotor_port)
                    WebSocketHandler.udp_send_number(motor_speed_right, 'localhost', WebSocketHandler.rightMotor_port)
                
                # 判断吸力是否需要更新
                if message_parts[2] != '-':
                    new_suction_num = int(message_parts[2])
                    # 更新存储速度
                    self.suction_num = new_suction_num
                    # 发送速度到马达驱动
                    WebSocketHandler.udp_send_number(new_suction_num * 10, 'localhost', WebSocketHandler.suctionMotor_port)

                # 回应客户端
                #await websocket.send(f"Echo: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if not websocket.open:
                # 停止机器人移动
                WebSocketHandler.udp_send_number(0, 'localhost', WebSocketHandler.leftMotor_port)
                WebSocketHandler.udp_send_number(0, 'localhost', WebSocketHandler.rightMotor_port)


def run_websockets_server(websocketPort, leftMotor_port, rightMotor_port, suctionMotor_port, websocket_logPrint):
    WebSocketHandler.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    WebSocketHandler.leftMotor_port = leftMotor_port
    WebSocketHandler.rightMotor_port = rightMotor_port
    WebSocketHandler.suctionMotor_port = suctionMotor_port

    WebSocketHandler.websocket_logPrint = websocket_logPrint


    # 运行websocket服务器
    handler_websocket = WebSocketHandler()
    start_server = websockets.serve(handler_websocket.connection_handling, "0.0.0.0", websocketPort)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
