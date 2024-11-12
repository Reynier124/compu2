import socketserver
import socket
import signal
import os
import argparse
import threading
from PIL import Image
from resize import Resize_image

class ForkingTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        all_info = self.request.recv(1024).decode()
        all_info = all_info.split(" -- ")

        path = all_info[0]
        scale = float(all_info[1])
        name = all_info[2]
        path_result = all_info[3]

        try:
            image = Image.open(path)
            result = Resize_image(image, scale).run()

            result.save(os.path.join(path_result.strip(), name.strip()))
            self.request.sendall(bytes(f"Se realizo correctamente \n", "utf-8"))

        except Exception as e:
            self.request.sendall(bytes(f"Error: {e} \n", "utf-8"))

class ForkingTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    
def start_server(address_family, host, port):
    ForkingTCPServer.address_family = address_family
    server = ForkingTCPServer((host, port), ForkingTCPRequestHandler)
    with server:
        print(f"Server started on {host}:{port}")
        server.serve_forever()

def cleanup(signum, frame):
    print("Shutting down server...")
    exit(0)
    


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    parser = argparse.ArgumentParser(description="Servidor TCP para el procesamiento de imagenes")
    parser.add_argument("--host4", type=str, default="localhost", help="Dirección IPv4 del servidor")
    parser.add_argument("--host6", type=str, default="::1", help="Dirección IPv6 del servidor")
    parser.add_argument("--port", type=int, default=7373, help="Puerto del servidor")
    args = parser.parse_args()

    thread_ipv4 = threading.Thread(target=start_server, args=(socket.AF_INET, args.host4, args.port), daemon=True)
    thread_ipv6 = threading.Thread(target=start_server, args=(socket.AF_INET6, args.host6, args.port), daemon=True)

    thread_ipv4.start()
    thread_ipv6.start()
    thread_ipv4.join()
    thread_ipv6.join()