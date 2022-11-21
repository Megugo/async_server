import asyncio
import json
import ast
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

reley_condition = {1:0,
                   2:0,
                   3:0,
                   4:0,
                   5:0,
                   6:0}

writers_for_broadcast = []

with open("f.txt", "r") as f:
    try:
        conditions = f.readline().strip("\n").split(" ")[:6]
        for i in reley_condition:
            reley_condition[i] = int(conditions[i-1])
    except IndexError:
        print("Error: Not enough values from reley file")
        exit(0)

class MyEventHandler(FileSystemEventHandler):
    def on_closed(self, event):
        if event.src_path == './f.txt':
            with open("f.txt", "r") as f:
                try:

                    conditions = f.readline().strip("\n").split(" ")[:6]
                    for i in reley_condition:
                        reley_condition[i] = int(conditions[i - 1])

                    status_broadcast()

                    print(f"Conditions change by reley:\n{json.dumps(reley_condition, indent=2)}")

                except IndexError:
                    print("Error: Not enough values from reley file")
                    exit(0)


def status_broadcast() -> None:
    json_reley_condition = json.dumps(reley_condition)
    for wrt in writers_for_broadcast:
        try:
            wrt.write(json_reley_condition.encode())
        except ConnectionError:
            print("wrong writer", wrt)


async def handler(reader: asyncio.StreamReader,writer: asyncio.StreamWriter)->None:
    out_data = None #json.dumps(reley_condition)
    #input_data = await reader.read(1024)
    #msg = input_data
    addr,port = writer.get_extra_info("peername")
    print(f"Addr:{addr}, port:{port}")
    broadcasting = False
    while True:
        raw_data = await reader.read(1000)#.decode()
        data = raw_data.decode('utf8').strip("\r\n").split(" ")#decode()

        command = data[0]
        #msg = data[1].replace("'", '"')
        print(data)

        #print(msg)

        if "1" in command and len(data)>1:
            msg = data[1].replace("'", '"')
            print("Before change",reley_condition)
            #json.loads(msg))
            try:
                #print("for dict",ast.literal_eval(msg))
                dict_msg = ast.literal_eval(msg)#json.loads(msg)
                print("for dict",dict_msg)
                if type(dict_msg) is dict:
                    print("for dict",dict_msg)
                    for i in dict_msg:
                        if (dict_msg[i] in [0,1]) and i in reley_condition.keys() :
                            reley_condition[i]= dict_msg[i]
                        else:
                            writer.write(f"Wrong key {i} or value {dict_msg[i]}".encode())
                    writer.write(b"Conditions changed")
                    print("After change",reley_condition)

                else:
                    writer.write(b"Not a dict")

                status_broadcast()

            except LookupError:
                writer.write(b"wrong dict")
                pass
            except SyntaxError:
                writer.write(b"wrong dict")
                pass
            except ValueError:
                writer.write(b"wrong dict")
                pass

        elif "2" == command and len(data)>1:
            writer.write(json.dumps(reley_condition).encode())

        elif "3" == command:

            if broadcasting == True:
                broadcasting = False
                writers_for_broadcast.remove(writer)
                writer.write(b"Broadcasting stoped")
                print(f"{addr} removed from broadcast")

            elif broadcasting == False:
                broadcasting = True
                writers_for_broadcast.append(writer)
                writer.write(b"Broadcasting started")
                print(f"{addr} added to broadcast")

        else: #command not in ["1","2","3"]:
            writer.write(b"Wrong command or not enough values")


        await writer.drain()

        if data == "exit" or not data[0]:
            if writer in writers_for_broadcast:
                writers_for_broadcast.remove(writer)
                print(f"{addr} removed from broadcast")
            break

    writer.close()



async def run_server() -> None:
    server = await asyncio.start_server(handler, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(MyEventHandler(), ".")  # , recursive=True)
    observer.start()

    asyncio.run(run_server())
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(run_server())

    observer.stop()
    observer.join()
