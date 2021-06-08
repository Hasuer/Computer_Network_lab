from socket import *
from threading import *
import tkinter
import tkinter.messagebox
import json
import struct
import os
import VoiceClient

import tkinter.filedialog
from tkinter import font
from tkinter.scrolledtext import ScrolledText

user = ''
user_id = -1
serverName = '172.16.120.177'
serverPort = 8888
users = list()


def login(*args):
    global user, user_id
    if not entryID.get():
        tkinter.messagebox.showerror('warning', '账号为空')
    elif not entryUSER.get():
        tkinter.messagebox.showerror('warning', '用户名为空')
    else:
        user_id = entryID.get()
        user = entryUSER.get()
        root.destroy()


root = tkinter.Tk()
root.geometry("320x210")
root.title("Login")
root.resizable(0, 0)
root.configure(background='DeepSkyBlue')

USER = tkinter.StringVar()
USER.set('')
ID = tkinter.StringVar()
ID.set('')

labelID = tkinter.Label(root, text='账号', bg="DeepSkyBlue")
labelID.place(x=40, y=45, width=70, height=40)
entryID = tkinter.Entry(root, width=80, textvariable=ID)
entryID.place(x=100, y=45, width=130, height=30)

labelUSER = tkinter.Label(root, text='用户名', bg="DeepSkyBlue")
labelUSER.place(x=40, y=100, width=70, height=40)
entryUSER = tkinter.Entry(root, width=80, textvariable=USER)
entryUSER.place(x=100, y=100, width=130, height=30)

loginButton = tkinter.Button(root, text='登陆', command=login, bg='Yellow')
loginButton.place(x=135, y=150, width=50, height=25)
root.bind('<Return>', login)
root.mainloop()
clientSocket = socket(AF_INET, SOCK_STREAM)


def doConnect():
    try:
        clientSocket.connect((serverName, serverPort))
    except error:
        print("connection failed! please try again later")
        exit()


doConnect()
clientSocket.send(json.dumps({
    'ID': user_id,
    'name': user
}).encode())

chatRoom = tkinter.Tk()
chatRoom.geometry("845x380")
chatRoom.title('chatroom')
chatRoom.resizable(0, 0)
megBox = ScrolledText(chatRoom)
megBox.place(x=5, y=0, width=640, height=320)

topFont = font.Font(size=20, slant=font.ITALIC)
messageFont = font.Font(family='Times', size=15)
megBox.tag_config('tag1', foreground='Blue', backgroun="yellow", font=topFont)
megBox.tag_config('tag2', font=messageFont)
megBox.insert(tkinter.END, '欢迎进入群聊!\n', 'tag1')

INPUT = tkinter.StringVar()
INPUT.set('')
entryInput = tkinter.Entry(chatRoom,
                           width=120,
                           textvariable=INPUT,
                           relief='sunken')
entryInput.place(x=5, y=320, width=600, height=50)

usersBox = tkinter.Listbox(chatRoom)
usersBox.place(x=600, y=0, width=120, height=320)
usersBox.insert(tkinter.END, "---当前在线用户---\n")
filesBox = tkinter.Listbox(chatRoom, cursor='based_arrow_down')
filesBox.place(x=720, y=0, width=115, height=320)
filesBox.insert(tkinter.END, "---资源文件列表---\n")


def download(*args):
    file_name = filesBox.get(filesBox.curselection())
    q = tkinter.messagebox.askyesno(title='下载', message='确认下载' + file_name)
    if q:
        headerInfo = {
            'req_type': 'download',
            'file_name': file_name
        }
        header = json.dumps(headerInfo).encode()
        clientSocket.send(struct.pack('i', len(header)))
        clientSocket.send(header)


def massSend(*args):
    message = entryInput.get().encode()
    if not message:
        tkinter.messagebox.showerror(title='错误', message='请输入内容！')
        return
    headerInfo = {
        'req_size': len(message),
        'req_type': 'group_message'
    }
    header = json.dumps(headerInfo).encode()
    clientSocket.send(struct.pack('i', len(header)))
    clientSocket.send(header)
    clientSocket.send(message)
    INPUT.set('')


def priSend():
    global users
    box = tkinter.Toplevel()
    box.geometry('200x200')
    group = tkinter.LabelFrame(box, text='选择私聊对象', padx=5, pady=5)
    group.pack(padx=10, pady=10)
    rank = tkinter.IntVar()
    for i in range(len(users)):
        if users[i][1] != user_id:
            tkinter.Radiobutton(group,
                                text=users[i][0],
                                variable=rank,
                                value=users[i][1]).pack(fill=tkinter.X)
    tkinter.Button(box, text='确认', command=box.destroy).pack()
    chatRoom.wait_window(box)
    message = INPUT.get().encode()
    req_userID = rank.get()
    if not message or not req_userID:
        return
    headerInfo = {
        'req_size': len(message),
        'req_type': 'private_message',
        'req_userID': req_userID
    }
    header = json.dumps(headerInfo).encode()
    clientSocket.send(struct.pack('i', len(header)))
    clientSocket.send(header)
    clientSocket.send(message)
    INPUT.set('')


def fileSend():
    file_name = tkinter.filedialog.askopenfilename()
    if not file_name:
        tkinter.messagebox.showerror(title='错误', message='没有选择任何文件')
        return
    fd = os.open(file_name, os.O_RDONLY)
    file_size = os.path.getsize(file_name)
    headerInfo = {
        'file_size': file_size,
        'req_type': 'upload',
        'file_name': file_name.split('/')[-1]
    }
    header = json.dumps(headerInfo).encode()
    clientSocket.send(struct.pack('i', len(header)))
    clientSocket.send(header)

    try:
        while True:
            file_data = os.read(fd, 1024)
            if file_data:
                clientSocket.send(file_data)
            else:
                break
    except Exception as e:
        print("传输异常: ", e)
    os.close(fd)


def receive():
    global users
    while True:
        try:
            header_length = struct.unpack('i', clientSocket.recv(4))[0]
        except error:
            if getattr(socket, '_closed'):
                print("log out")
                break
            else:
                print("socket error,reconnect...")
                doConnect()
                continue

        header = clientSocket.recv(header_length)
        headerInfo = json.loads(header.decode())
        data_size = headerInfo['data_size']
        data_type = headerInfo['data_type']
        if data_type == 'file':
            fd = os.open('res/' + headerInfo['file_name'], os.O_RDWR | os.O_CREAT)
            recv_size = 0

            while recv_size + 1024 < data_size:
                recv_data = clientSocket.recv(1024)
                os.write(fd, recv_data)
                recv_size += len(recv_data)
            os.write(fd, clientSocket.recv(data_size - recv_size))
            tkinter.messagebox.showinfo(title='下载', message='下载完成')
            continue
        res = b''
        recv_size = 0
        while recv_size + 1024 < data_size:
            recv_data = clientSocket.recv(1024)
            res += recv_data
            recv_size += len(recv_data)
        res += clientSocket.recv(data_size - recv_size)

        if data_type == 'message':
            megBox.insert(tkinter.END, res.decode() + '\n', 'tag2')

        elif data_type == 'users_list':
            users = json.loads(res.decode())
            usersBox.delete(1, tkinter.END)
            for i in range(len(users)):
                usersBox.insert(tkinter.END, users[i][0])

        elif data_type == 'files_list':
            files = json.loads(res.decode())
            filesBox.delete(1, tkinter.END)
            for i in range(len(files)):
                filesBox.insert(tkinter.END, files[i])


def fileRecv(file_name, file_size):
    fd = os.open('res/' + file_name, os.O_RDWR | os.O_CREAT)
    recv_size = 0

    while recv_size < file_size:
        recv_data = clientSocket.recv(1024)
        os.write(fd, recv_data)
        recv_size += len(recv_data)

    tkinter.messagebox.showinfo(title='下载', message='下载完成')


filesBox.bind('<<ListboxSelect>>', download)
massSendBtn = tkinter.Button(chatRoom,
                             command=massSend,
                             text="发送",
                             font=('Helvetica', 18),
                             fg='Blue',
                             bg='white')
massSendBtn.place(x=600, y=320, width=60, height=50)
priSendBtn = tkinter.Button(chatRoom,
                            command=priSend,
                            text="私聊",
                            font=('Helvetica', 18),
                            fg='Blue',
                            bg='white')
priSendBtn.place(x=660, y=320, width=60, height=50)
chatRoom.bind('<Return>', massSend)
fileSendBtn = tkinter.Button(chatRoom,
                             command=fileSend,
                             text="上传",
                             font=('Helvetica', 18),
                             fg='Blue',
                             bg='white')
fileSendBtn.place(x=720, y=320, width=60, height=50)


def startVoice():
    tkinter.messagebox.showinfo(title='语音聊天', message='您已进入语音聊天室')
    voiceThread = Thread(target=voice)
    voiceThread.setDaemon(True)
    voiceThread.start()


def voice():
    VoiceClient.VoiceClient()


voiceBtn = tkinter.Button(chatRoom,
                          command=startVoice,
                          text="语音",
                          font=('Helvetica', 18),
                          fg='Blue',
                          bg='white')
voiceBtn.place(x=780, y=320, width=60, height=50)

recThread = Thread(target=receive)
recThread.setDaemon(True)

recThread.start()
chatRoom.mainloop()
clientSocket.close()
