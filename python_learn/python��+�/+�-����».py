import socket
import threading
import sys
import nturl2path

class HttpWebServer(object):
    def __init__(self, port):
        # 创建tcp服务端套接字
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定端口号
        tcp_server_socket.bind(('', port))
        # 设置监听
        tcp_server_socket.listen(128)
        self.tcp_server_socket = tcp_server_socket

    @staticmethod
    def handle_client_request(service_client_socket, ip_port):
        recv_data = service_client_socket.recv(4096)
        if len(recv_data) == 0:
            print('浏览器关闭了')
            service_client_socket.close()
            return
        recv_content = recv_data.decode('utf-8')
        # print(recv_content)

        request_list = recv_content.split(' ', maxsplit=2)
        # print(request_list[1])

        if request_list[1] == '/':
            request_list[1] = '/index.html'

        filename = nturl2path.url2pathname(request_list[1])

        try:
            with open('.' + filename, 'rb') as file:
                # 读取文件数据
                file_data = file.read()
        except Exception as e:
            # 404
            # 响应行
            response_line = 'HTTP/1.1 404 File not found\r\n'

            # 响应头
            response_header = 'Server: PWS1.0\r\n'

            # 响应体
            with open('error.html', 'rb') as errfile:
                errdata = errfile.read()
            response_body = errdata

            # 拼接响应报文
            response_data = (response_line + response_header + '\r\n').encode('utf-8') + response_body

            # 发送数据
            service_client_socket.send(response_data)
        else:
            # 返回文件
            # 响应行
            response_line = 'HTTP/1.1 200 OK\r\n'

            # 响应头
            response_header = 'Server: PWS1.0\r\n'

            # 响应体
            response_body = file_data

            # 拼接响应报文
            response_data = (response_line + response_header + '\r\n').encode('utf-8') + response_body

            # 发送数据
            service_client_socket.send(response_data)
        finally:
            # 关闭套接字
            service_client_socket.close()
    def start(self):
        while True:
            # 等待客户端的连接请求
            service_client_socket, ip_port = self.tcp_server_socket.accept()

            service_client_thread = threading.Thread(target=HttpWebServer.handle_client_request,
                                                     args=(service_client_socket, ip_port))
            service_client_thread.setDaemon(True)
            service_client_thread.start()

def main():
    if len(sys.argv) < 2:
        print('执行命令如下：python xxxx.py 9000')
        return
    if not sys.argv[1].isdigit():
        print('端口号不合法！')
        return
    port = int(sys.argv[1])
    if port > 65535 or port <= 0:
        print('端口号不合法！')
        return
    httpWebServer = HttpWebServer(port)
    httpWebServer.start()
if __name__ == '__main__':
    main()

