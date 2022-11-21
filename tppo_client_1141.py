import asyncio

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    message =""
    #data_input = await get_steam_reader(sys.stdin)
    while True:
        message = input()#await ainput("")
        if message == "exit":
            break
        if message:
            print(f'Send: {message}')
            writer.write(message.encode())

        if message == '3':
            while True:
                try:
                    data = await reader.read(100)
                    if data!=b"":
                        print(f'Received: {data.decode()!r}')
                except BaseException:#KeyboardInterrupt:
                    print("closing")
                    writer.write(b"3")
                    break
        await writer.drain()
        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

    print('Close the connection')

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client())
