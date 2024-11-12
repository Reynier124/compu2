import asyncio
import signal
import argparse
from aiohttp import web

def cleanup(signum, frame):
    print("Finish the process")
    loop = asyncio.get_running_loop()
    loop.stop()
    exit()

class AsyncConnection:
    def __init__(self, host, port, a_host, a_port):
        self.host = host
        self.port = port
        self.a_host = a_host
        self.a_port = a_port
        self.app = web.Application()
        self.app.router.add_post('/process_image', self.handle_post)

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

    async def handle_post(self, request):
        data = await request.json()
        path = data['path']
        scale = data['scale']
        name = data['name']
        path_result = data['path_result']

        all_info = f"{path} -- {scale} -- {name} -- {path_result}"

        processed_image = await self.send_image_to_server(all_info)

        return web.Response(text=processed_image)

    async def send_image_to_server(self, image):
        server_host = self.a_host
        server_port = self.a_port

        reader, writer = await asyncio.open_connection(server_host, server_port)

        writer.write(image.encode())
        await writer.drain()

        data = await reader.read(1024)
        response = data.decode()

        writer.close()
        await writer.wait_closed()

        return response

async def main():
    parser = argparse.ArgumentParser(description="Servidor HTTP asíncrono para clientes")
    parser.add_argument("--host", type=str, default="::", help="Dirección IP del servidor")
    parser.add_argument("--port", type=int, default=8080, help="Puerto del servidor")
    parser.add_argument("--Ahost", type=str, default="localhost", help="Dirección IP del servidor de procesamiento de imágenes")
    parser.add_argument("--Aport", type=int, default=7373, help="Puerto del servidor de procesamiento de imágenes")
    args = parser.parse_args()
    HOST, PORT = args.host, args.port
    Ahost, Aport = args.Ahost, args.Aport
    signal.signal(signal.SIGINT, cleanup)
    conn = AsyncConnection(HOST, PORT, Ahost, Aport)
    await conn.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
