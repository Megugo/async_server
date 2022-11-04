import asyncio

async def handler(reader: asyncio.StreamReader,writer: asyncio.StreamWriter)->None:
    data = None
    
    #while data != 'srwgte':
    data = await reader.read(1024)
    msg = data.decode()
    addr,port = writer.get_extra_info("peername")
    print(f"Message:{msg}, Addr:{addr}, port:{port}")
    await asyncio.sleep(3)
    writer.write(data)
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def run_server() -> None:
    server = await asyncio.start_server(handler, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_server())