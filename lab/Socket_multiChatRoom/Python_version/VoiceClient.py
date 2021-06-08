import socket
import threading
import pyaudio


class VoiceClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                self.target_ip = '172.16.120.177'
                self.target_port = 9808
                self.s.connect((self.target_ip, self.target_port))
                break
            except Exception as e:
                print("Couldn't connect to server", e)

        chunk_size = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 44100

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data)
        receive_thread.setDaemon(True)
        receive_thread.start()
        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            try:
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except Exception:
                pass

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except Exception:
                pass

