"""
作用: picamera driver
作者: Jianjun Lang
日期: 2024/11/14
版本: v3.6
更多描述:
更新:
3.6
使用tcp服务器, 支持多用户同时使用实时视频
修复断连bug
"""

import io
import picamera
import threading
import socket

''' video stream handler '''
class StreamingOutputHandler(object):
    def __init__(self):
        self.frame = None
        # 类似文件的对象，用于处理字节数据 (内存)
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, frameChunk):
        if frameChunk.startswith(b'\xff\xd8'):
            '''receive new frame'''
            with self.condition:
                # 提取前一帧放入共享空间
                self.frame = self.buffer.getvalue()
                # notify waiting thread
                self.condition.notify_all()
            
            '''清空buffer'''
            # move filePointer to file begining
            self.buffer.seek(0)
            # delete all data after filePointer
            self.buffer.truncate()
        
        # 一般情况: 写入帧片段到buffer
        return self.buffer.write(frameChunk)

''' client线程处理函数: 不断发送帧到client '''
def handle_client(client_socket, streamingOutputHandler):
    end_marker = b"<END_OF_FILE>"
    try:
        while True:
            '''等待并获取下一帧'''
            with streamingOutputHandler.condition:
                # wait signal from "self.condition.notify_all()"
                streamingOutputHandler.condition.wait()
                frame = streamingOutputHandler.frame
            
            client_socket.sendall(frame + end_marker)
            
    except (BrokenPipeError, ConnectionResetError):
        # 视频连接中断
        # 客户端的连接被意外关闭了
        pass
    finally:
        client_socket.close()

''' 启动TCP server: 接收连接, 启动线程处理连接 '''
def start_server(streamingOutputHandler, acceptAddress = '0.0.0.0', serverPort=8000):
    # creat, bind, listen to socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((acceptAddress, serverPort))
    server_socket.listen(5)

    while True:
        # accpet client connect
        client_socket, addr = server_socket.accept()

        # create + start a new thread for handling
        client_thread = threading.Thread(target=handle_client, args=(client_socket, streamingOutputHandler))
        client_thread.start()

''' 运行摄像机和服务器 '''
def run_picamera_driver(serverPort_video):
    with picamera.PiCamera(resolution='720x360', framerate=24) as camera:
        camera.rotation = 0

        # 启动picam视频流
        streamingOutputHandler = StreamingOutputHandler()
        camera.start_recording(streamingOutputHandler, format='mjpeg')

        # 启动服务器
        start_server(streamingOutputHandler, serverPort=serverPort_video)
