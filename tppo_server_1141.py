import asyncio
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

reley_condition = {1:0,
                   2:0,
                   3:0,
                   4:0,
                   5:0,
                   6:0}

with open("f.txt", "r") as f:
    try:
        conditions = f.readline().strip("\n").split(" ")[:6]
        for i in reley_condition:
            reley_condition[i] = conditions[i-1]
    except IndexError:
        print("Error: Not enough values from reley file")
        exit(0)

class MyEventHandler(FileSystemEventHandler):
    def on_closed(self, event):
        global to_out
        if event.src_path == './f.txt':
            with open("f.txt", "r") as f:
                try:

                    conditions = f.readline().strip("\n").split(" ")[:6]
                    for i in reley_condition:
                        reley_condition[i] = conditions[i - 1]
                    print(f"Conditions change by reley:\n{json.dumps(reley_condition, indent=2)}")

                except IndexError:
                    print("Error: Not enough values from reley file")
                    exit(0)

async def handler(reader: asyncio.StreamReader,writer: asyncio.StreamWriter)->None:
    out_data = None #json.dumps(reley_condition)
    input_data = await reader.read(1024)
    msg = input_data
    addr,port = writer.get_extra_info("peername")
    print(f"Message:{msg}, Addr:{addr}, port:{port}")
    if input_data == b"2":
        out_data = json.dumps(reley_condition)
    else:
        out_data = "wrong command"
    writer.write(out_data.encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def run_server() -> None:
    server = await asyncio.start_server(handler, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(MyEventHandler(), ".")  # , recursive=True)
    observer.start()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_server())

    observer.stop()
    observer.join()
