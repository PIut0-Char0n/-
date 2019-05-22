from socket import *
import sys
from time import sleep


# 具体功能
class FtpClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    def do_list(self):
        """
         查看列表
        :return:
        """
        self.sockfd.send(b'L')  # 发送请求
        # 等待回复
        data = self.sockfd.recv(128).decode()
        # OK表示请求成功
        if data == 'OK':
            data = self.sockfd.recv(4096)
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        """
         退出客户端
        :return:
        """
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit('谢谢使用')

    def do_get(self, filename):
        """
         下载文件
        :param filename:
        :return:
        """
        # 发送请求获取类型文件
        self.sockfd.send(('G ' + filename).encode())
        data = self.sockfd.recv(1024).decode()
        if data == 'OK':
            fd = open(filename, 'wb')
            # 接收内容写入文件
            while True:
                data = self.sockfd.recv(1024)
                if data == b'##':
                    break
                fd.write(data)
            fd.close()
        else:
            print(data)

    def do_put(self, filename):
        """
         上传文件
        :param filename:
        :return:
        """
        try:
            fd = open(filename, 'rb')
        except Exception:
            print("没有改文件")
            return
        filename = filename.split('/')[-1]
        self.sockfd.send(('P ' + filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = fd.read(1024)
                if not data:
                    sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            fd.close()
        else:
            print(data)


def request(s):
    """
    发起请求
    :param s:
    :return:
    """
    ftp = FtpClient(s)
    while True:
        print('\n==============命令选项============')
        print('............list..............')
        print('----------get file------------')
        print('************put file**********')
        print('++++++++++++quit+++++++++++++++')
        print('==================================')

        cmd = input("输入命令:")
        if cmd.strip() == 'list':
            ftp.do_list()
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)


def main():
    """
    网络连接
    :return:
    """
    # 服务器地址
    ADDR = ('127.0.0.1', 8888)
    s = socket()
    try:
        s.connect(ADDR)
    except Exception:
        print("连接服务器失败")
        return
    else:
        print("""*************************
Data   File   Image
*************************
        """)
        cls = input('请输入文件种类:')
        if cls not in ['data', 'file', 'image']:
            print('Sorry input error')
            return
        else:
            s.send(cls.encode())
            request(s)


if __name__ == '__main__':
    main()
