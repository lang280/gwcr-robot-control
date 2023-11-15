"""
Purpose: HTTP Server for Image Transmission (Camera Driver) and Robot Control
Author: Jianjun Lang
Date: October 30, 2024
Version: v3.6
Additional Description:
Updates:
Established a connection with the camera driver using TCP to allow multiple video stream simultaneously
"""
from http import server
import socketserver
import mimetypes
import socket

# HTTP请求处理
class HandlerHTTP(server.BaseHTTPRequestHandler):
    videoServer_ip = None
    videoServer_port = None
    video_endMarker = None
    httpPath = None
    websocketPort = None
    httpLogging = None
    
    # 控制logging打印
    def log_message(self, format, *args):
        if HandlerHTTP.httpLogging == 1:
            # 只打印错误logging
            if "200" not in format % args:
                # 父类方法打印
                super().log_message(format, *args)
        elif HandlerHTTP.httpLogging == 2:
            # 打印所有logging
            # 父类方法打印
            super().log_message(format, *args)
        else:
            # 什么都不打印
            pass

    def do_GET(self):
        try:
            if self.path == '/stream.mjpg':
                # 视频请求
                # 从camera driver获取视频流发往网页控制端

                # 发送视频status codes, http头
                self.send_response(200)
                headers = {
                    'Age': '0',
                    # 确保不缓存视频流
                    'Cache-Control': 'no-cache, private',
                    # 旧式的不缓存指令
                    'Pragma': 'no-cache',
                    # 内容类型标明是一个MJPEG流
                    'Content-Type': 'multipart/x-mixed-replace; boundary=FRAME'
                }
                for header, value in headers.items():
                    self.send_header(header, value)
                self.end_headers()       
                
                frameBuffer = b''
                try:
                    # connet to camera server as client
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((HandlerHTTP.videoServer_ip, HandlerHTTP.videoServer_port))
                    while True:
                        '''accept frame from camera server'''
                        while True:
                            frameChunk = client_socket.recv(4096)
                            if HandlerHTTP.video_endMarker in frameChunk:
                                # reach end of chunk
                                splitChunk = frameChunk.split(HandlerHTTP.video_endMarker)
                                frame = frameBuffer + splitChunk[0]
                                frameBuffer = splitChunk[1]
                                break
                            else:
                                frameBuffer += frameChunk
                        

                        '''send frame to http client'''
                        # 发送帧http头
                        self.wfile.write(b'--FRAME\r\n')  # 写入MJPEG分隔符
                        self.send_header('Content-Type', 'image/jpeg')  # 帧的内容类型为JPEG
                        self.send_header('Content-Length', len(frame))  # 图片帧的长度（字节）
                        self.end_headers()  # 结束头部信息

                        # 发送帧内容
                        self.wfile.write(frame)
                        # 发送帧的结束
                        self.wfile.write(b'\r\n')
                except BrokenPipeError:
                    pass
                
            else:
                # 通用类请求

                # file path on server
                if self.path == '/':
                    # homepage
                    file_path = HandlerHTTP.httpPath + '/web_page.html'
                else: 
                    file_path = HandlerHTTP.httpPath + self.path

                # 找出文件类型
                file_mime_type = mimetypes.guess_type(file_path)[0]

                if file_mime_type.startswith('text'):
                    # 文本文件
                    with open(file_path, 'r') as file:
                        # 提取文本内容
                        file_string = file.read()

                        # 更新html中的websocket
                        if self.path == '/':
                            # 在html文件中设置websocket端口号
                            file_string = file_string.format(placeholder_websocketPort=(":" + str(HandlerHTTP.websocketPort)))
                        
                        # 以utf-8编码成byte
                        file_content = bytes(file_string, 'utf-8')
                else:
                    # 二进制文件
                    with open(file_path, 'rb') as file:
                        file_content = file.read()
                
                
                # 发送HTTP status codes
                self.send_response(200)
                # 发送Response Header
                self.send_header('Content-Type', file_mime_type)
                self.end_headers() # 发送CRLF 结束头字段

                # 发送请求文件
                self.wfile.write(file_content)
        
        
        except FileNotFoundError as e:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(str(e) + "\r\n", 'utf-8'))
        
        except OSError:
            # 客户端在服务器发送响应之前关闭了连接
            pass
        
        except Exception as e:
            print(e)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(bytes(str(e) + "\r\n", 'utf-8'))
        


# HTTP服务器
# 继承自socketserver模块的ThreadingMixIn类和http.server模块的HTTPServer类
class ServerHTTP(socketserver.ThreadingMixIn, server.HTTPServer):
    # 设置允许地址复用。当服务器重启时，可以无需等待先前使用的端口释放，直接复用端口。
    allow_reuse_address = True
    # 指定服务器所启动的线程是守护线程(daemon threads)。这意味着主程序结束时，不会等待这些线程终止。
    daemon_threads = True

def run_http_server(httpPort, httpPath, httpLogging, websocketPort, videoServer_ip, videoServer_port, video_endMarker):
    HandlerHTTP.httpPath = httpPath
    HandlerHTTP.websocketPort = websocketPort
    HandlerHTTP.videoServer_ip = videoServer_ip
    HandlerHTTP.videoServer_port = videoServer_port
    HandlerHTTP.video_endMarker = video_endMarker
    HandlerHTTP.httpLogging = httpLogging
    # 创建服务器, 输入地址端口
    server = ServerHTTP(('0.0.0.0', httpPort), HandlerHTTP)
    server.serve_forever()
