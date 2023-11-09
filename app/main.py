# git_http_server
import socket
import threading
import os
import argparse

#def handler(connection, address):
def handler(connection, address, args):
    data = connection.recv(1024)
    if data:
        start_line = data.decode().split("\r\n")[0]
        method, path, version = start_line.split(" ")
        headers = {}
        for line in data.decode().split("\r\n")[1:]:
            if line:
                key, value = line.split(": ")
                headers[key.lower()] = value
            else:
                break                
        print(method, path, version)
        
        if method == "GET":
            if path == "/":
                connection.sendall("HTTP/1.1 200 OK\r\n\r\n".encode())
            elif path.startswith("/echo"):
                message = path.split("/echo/")[1]
                length = len(message)
                connection.sendall(
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{message}".encode()
                )
            elif path == "/user-agent":
                message = headers["user-agent"]
                length = len(message)
                connection.sendall(
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{message}".encode()
                )
            elif path.startswith("/files"):
                filename = path.split("/files/")[1]
                if os.path.isfile(f"{args.directory}/{filename}"):
                    content = open(f"{args.directory}/{filename}", "r").read()
                    message = "HTTP/1.1 200 OK\r\n"
                    message += f"Content-Type: application/octet-stream\r\n"
                    message += f"Content-Length: {len(content)}\r\n"
                    message += "\r\n"
                    message += content
                    connection.sendall(message.encode())
                else:
                    connection.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            else:
                connection.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        elif method == "POST":
            if path.startswith("/files"):
                filename = path.split("/files/")[1]
                content = data.decode().split("\r\n\r\n")[1]
                with open(f"{args.directory}/{filename}", "w") as f:
                    f.write(content)
                connection.sendall("HTTP/1.1 201 OK\r\n\r\n".encode())                
            else:
                connection.sendall("HTTP/1.1 404 Not Found\r\n\r\n".encode())            

        connection.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, help="the directory path")
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221))

    while True:
        print("awaiting connection")
        
        connection, address = server_socket.accept()
        threading.Thread(target=handler, args=(connection, address, args)).start()
        
if __name__ == "__main__":
    main()
