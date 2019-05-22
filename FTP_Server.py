"""
    ftp文件服务器
    并发网络功能训练
"""
from socket import *
from threading import Thread
import sys, os
from time import sleep

# 全局变量
ADDR = ('0.0.0.0', 8888)
FTP = '/home/tarena/month02/FTP/'  # 文件库路径


# 将客户端请求功能封装成类
class FtpServer:
    def __init__(self, connfd, FTP_PATH):
        self.connfd = connfd
        self.path = FTP_PATH

    def do_list(self):
        """
         获取文件下载列表
        :return:
        """
        files = os.listdir(self.path)
        if not files:
            self.connfd.send('该文件类别空'.encode())
            return
        else:
            self.connfd.send(b'OK')
        fs = ' '
        for file in files:
            # 屏蔽隐藏文件 和筛选普通文件
            if file[0] != '.' and os.path.isfile(self.path + file):
                fs += file + '\n'
                self.connfd.send(fs.encode())

    def do_get(self, filename):
        """
         下载文件
        :param filename:
        :return:
        """
        try:
            fd = open(self.path + filename, 'rb')
        except Exception as e:
            print(e)
            return
        else:
            self.connfd.send(b'OK')
            sleep(0.1)
        while True:
            data = fd.read(1024)
            if not data:
                sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)

    def do_put(self, filename):
        """
         上传文件
        :param filename:
        :return:
        """
        if os.path.exists(self.path + filename):
            self.connfd.send("该文件已存在").encode()
            return
        self.connfd.send(b'OK')
        fd = open(self.path + filename, 'wb')
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            fd.write(data)
        fd.close()


def handle(connfd):
    """
    客户端请求处理函数
    :param connfd:
    :return:
    """
    # 选择文件夹
    cls = connfd.recv(1024).decode()
    FTP_PATH = FTP + cls + '/'
    ftp = FtpServer(connfd, FTP_PATH)
    while True:
        # 接受客户端请求
        data = connfd.recv(1024).decode()
        if not data or data[0] == 'Q':
            return
        elif data[0] == 'L':
            ftp.do_list()
        elif data[0] == 'G':
            filename = data.split(' ')[-1]
            ftp.do_get(filename)
        elif data[0] == 'P':
            filename = data.split(' ')[-1]
            ftp.do_put(filename)


def main():
    """
    网络搭建
    :return:
    """
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)
    print("Listen the port 8888...")

    while True:
        try:
            connfd, addr = s.accept()
        except KeyboardInterrupt:
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue
        print('连接的客户端：', addr)
        # 创建线程处理请求
        client = Thread(target=handle, args=(connfd,))
        client.setDaemon(True)
        client.start()


if __name__ == '__main__':
    main()
