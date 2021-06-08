from socket import *
from threading import *
import select
import queue
import json
import struct
import os
import VoiceServer

users_list = list()


class User:
    """user_info"""

    def __init__(self, ID, name, mSocket):
        self.user_id = ID
        self.user_name = name
        self.socket = mSocket
        users_list.append(self)


def onlineUsers():
    onlineList = ['users_list']
    for i in range(len(users_list)):
        onlineList.append((users_list[i].user_name, users_list[i].user_id))
    return onlineList


def ableDocs():
    docsList = ['files_list']
    docsList.extend(os.listdir())
    return docsList


def newUser(ID, name, mSocket):
    new_user = User(ID, name, mSocket)
    return new_user


def sendData():
    while True:
        if not messages_queue.empty():
            Data = messages_queue.get()
            if isinstance(Data, str):
                Data = Data.encode()
                for i in range(len(users_list)):
                    headerInfo = {
                        'data_size': len(Data),
                        'data_type': 'message'
                    }
                    header = json.dumps(headerInfo).encode()
                    users_list[i].socket.send(struct.pack('i', len(header)))
                    users_list[i].socket.send(header)
                    users_list[i].socket.send(Data)
            elif isinstance(Data, list):
                Type = Data[0]
                Data.pop(0)
                Info = json.dumps(Data).encode()
                for i in range(len(users_list)):
                    headerInfo = {
                        'data_size': len(Info),
                        'data_type': Type
                    }
                    header = json.dumps(headerInfo).encode()
                    users_list[i].socket.send(struct.pack('i', len(header)))
                    users_list[i].socket.send(header)
                    users_list[i].socket.send(Info)


def fileSend(client, file_name):
    doc = os.open(file_name, os.O_RDONLY)
    file_size = os.path.getsize(file_name)
    headerInfo = {
        'data_size': file_size,
        'data_type': 'file',
        'file_name': file_name
    }
    header = json.dumps(headerInfo).encode()
    client.socket.send(struct.pack('i', len(header)))
    client.socket.send(header)

    try:
        while True:
            file_data = os.read(doc, 1024)
            if file_data:
                client.socket.send(file_data)
            else:
                break
    except Exception as e:
        print("传输异常: ", e)
    os.close(doc)


def fileRecv(client, file_name, file_size):
    nfd = os.open(file_name, os.O_RDWR | os.O_CREAT)
    recv_size = 0

    while recv_size + 1024 < file_size:
        recv_data = client.socket.recv(1024)
        os.write(nfd, recv_data)
        recv_size += len(recv_data)

    os.write(nfd, client.socket.recv(file_size - recv_size))
    print("接收文件完成!")
    messages_queue.put(ableDocs())


def receive(client, header_data):
    header_length = struct.unpack('i', header_data)[0]
    header = client.socket.recv(header_length)
    headerInfo = json.loads(header.decode())
    req_type = headerInfo['req_type']

    if req_type == 'download':
        file_name = headerInfo['file_name']
        fileThread = Thread(target=fileSend, args=(client, file_name))
        fileThread.start()
        return

    if req_type == 'upload':
        file_name = headerInfo['file_name']
        file_size = headerInfo['file_size']
        fileRecv(client, file_name, file_size)
        return

    res = b''
    req_size = headerInfo['req_size']
    recv_size = 0
    while recv_size + 1024 < req_size:
        recv_data = client.socket.recv(1024)
        res += recv_data
        recv_size += len(recv_data)

    res += client.socket.recv(req_size - recv_size)

    if req_type == 'group_message':
        message = client.user_name + ' : ' + res.decode()
        messages_queue.put(message)

    elif req_type == 'private_message':
        req_userID = headerInfo['req_userID']
        for man in users_list:
            if man.user_id == req_userID:
                message = client.user_name + ' 对 ' + man.user_name + ' : ' + res.decode()
                message = message.encode()
                headerInfo = {
                    'data_size': len(message),
                    'data_type': 'message'
                }
                header = json.dumps(headerInfo).encode()
                man.socket.send(struct.pack('i', len(header)))
                man.socket.send(header)
                man.socket.send(message)

                client.socket.send(struct.pack('i', len(header)))
                client.socket.send(header)
                client.socket.send(message)
                break


serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_addr = ('', 8888)
serverSocket.bind(server_addr)
serverSocket.listen(10)
serverSocket.setblocking(False)

os.chdir('resources')

vServer = VoiceServer.VoiceServer()
vServer.start()


timeout = 10
epoll = select.epoll()  # epoll对象
epoll.register(serverSocket.fileno(), select.EPOLLIN)
messages_queue = queue.Queue()
# 文件句柄到所对应对象的字典 句柄：对象
fd_to_socket = {serverSocket.fileno(): serverSocket, }

sendThread = Thread(target=sendData)
sendThread.setDaemon(True)
sendThread.start()

while True:
    print("waiting for connection")
    # 轮询注册的事件集合，返回值为[(文件句柄，对应的事件)，(...),....]
    events = epoll.poll(timeout)
    if not events:
        print("epoll超时，没有指定时间发生，重新轮询")
        continue
    print(len(events), "new events!")

    for fd, event in events:
        # 欢迎套接字发生事件，说明有新连接

        if fd == serverSocket.fileno():
            connectSocket, address = serverSocket.accept()
            print("New connection!")
            loginInfo = connectSocket.recv(1024).decode()
            userInfo = json.loads(loginInfo)
            user = newUser(userInfo['ID'], userInfo['name'], connectSocket)
            epoll.register(connectSocket.fileno(), select.EPOLLIN)
            fd_to_socket[connectSocket.fileno()] = user
            messages_queue.put("---欢迎 " + user.user_name + " 进入聊天室---")
            messages_queue.put(onlineUsers())
            messages_queue.put(ableDocs())

        # 关闭事件
        elif event & select.EPOLLHUP:
            print('client closed the connection')
            # 在epoll中注销客户端句柄
            epoll.unregister(fd)
            # 关闭客户端的文件句柄?关闭套接字
            fd_to_socket[fd].socket.close()
            users_list.remove(fd_to_socket[fd])
            # 删除信息 ?
            del fd_to_socket[fd]
            messages_queue.put(onlineUsers())

        # 可读事件
        elif event & select.EPOLLIN:
            # 接收数据
            data = fd_to_socket[fd].socket.recv(4)
            if data:
                print("收到数据")
                receive(fd_to_socket[fd], data)
            else:
                print('Client closed the connection')
                epoll.unregister(fd)
                fd_to_socket[fd].socket.close()
                users_list.remove(fd_to_socket[fd])
                del fd_to_socket[fd]
                messages_queue.put(onlineUsers())

epoll.unregister(serverSocket.fileno())
epoll.close()
serverSocket.close()
