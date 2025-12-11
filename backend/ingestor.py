import asyncio
from typing import Optional
from .storage import LogStorage

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, storage: LogStorage, loop: asyncio.AbstractEventLoop):
        self.storage = storage
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode('utf-8', errors='ignore')
        # Schedule the storage add_log coroutine
        asyncio.run_coroutine_threadsafe(
            self.storage.add_log(message, "UDP", addr[0]),
            self.loop
        )

class LogIngestor:
    def __init__(self, storage: LogStorage, udp_port: int = 9000, tcp_port: int = 9001):
        self.storage = storage
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.udp_transport = None
        self.tcp_server = None

    async def start(self):
        loop = asyncio.get_running_loop()
        
        # Start UDP Server
        self.udp_transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self.storage, loop),
            local_addr=('0.0.0.0', self.udp_port)
        )
        print(f"UDP Log Ingestor started on port {self.udp_port}")
        
        # Start TCP Server
        self.tcp_server = await asyncio.start_server(
            self.handle_tcp_client, '0.0.0.0', self.tcp_port
        )
        print(f"TCP Log Ingestor started on port {self.tcp_port}")
        # Not awaiting server.serve_forever() here to allow main loop to continue,
        # but we need to ensure the server keeps running.
        # Actually server_forever blocks, so we usually run these as tasks or use start_server which returns a server object.
        # Background task for serving is needed if we want to return.
        asyncio.create_task(self.tcp_server.serve_forever())

    async def handle_tcp_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        try:
            while True:
                data = await reader.readline()
                if not data:
                    break
                message = data.decode('utf-8', errors='ignore')
                await self.storage.add_log(message, "TCP", addr[0])
        except Exception as e:
            print(f"TCP Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def stop(self):
        if self.udp_transport:
            self.udp_transport.close()
        if self.tcp_server:
            self.tcp_server.close()
            await self.tcp_server.wait_closed()
