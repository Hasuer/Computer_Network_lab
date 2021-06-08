import socket
import threading


class VoiceServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        while True:
            try:
                self.port = 9808
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.bind(('', self.port))
                break
            except:
                print("Couldn't bind to that port")
        self.connections = []

    def run(self):
        self.s.listen(100)
        while True:
            c, addr = self.s.accept()
            print("语音聊天新用户！")
            self.connections.append(c)
            threading.Thread(target=self.handle_client, args=(c,)).start()

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self, c):
        while 1:
            try:
                data = c.recv(1024)
                self.broadcast(c, data)

            except socket.error:
                c.close()

