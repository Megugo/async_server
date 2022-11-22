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

prev_condition = {}

writers_for_broadcast = []

json_out = {"data":""}

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

                    print(f"Conditions changed:\n{json.dumps(reley_condition, indent=2)}")

                except IndexError:
                    print("Error: Not enough values from reley file")
                    exit(0)


def status_broadcast() -> None:
    json_out["data"] = json.dumps(reley_condition)

    for wrt in writers_for_broadcast:
        try:
            send_json(wrt,json_out)
        except ConnectionError:
            print("wrong writer", wrt)

def send_json(writer,json_dict):
    writer.write(json.dumps(json_dict).encode())

async def handler(reader: asyncio.StreamReader,writer: asyncio.StreamWriter)->None:
    out_data = None
    addr,port = writer.get_extra_info("peername")
    print(f"Connected: Addr:{addr}, port:{port}\n")
    broadcasting = False


    while True:
        raw_data = await reader.read(1000)
        data = json.loads(raw_data)
        command = data["command"]
        print(f"Received data: {data}\n")

        if "1" in command and len(data)>1:
            msg = data["data"]
            prev_condition = reley_condition.copy()
            try:
                dict_msg = ast.literal_eval(msg)
                if type(dict_msg) is dict:
                    for i in dict_msg:
                        if (dict_msg[i] in [0,1]) and i in reley_condition.keys() :
                            reley_condition[i]= dict_msg[i]

                    if prev_condition!=reley_condition:
                        json_out["data"] = "Conditions changed"
                        send_json(writer,json_out)
                        with open("f.txt", "w") as f:
                            str_conditions =" ".join(str(reley_condition[c]) for c in reley_condition)
                            f.write(str_conditions)

                    else:
                        json_out["data"] = "Nothing changed"
                        send_json(writer,json_out)

                else:
                    json_out["data"] = "Not a dict"
                    send_json(writer,json_out)

            except LookupError or SyntaxError or ValueError:
                json_out["data"] = "wrong dict"
                send_json(writer,json_out)

        elif "2" == command and len(data)>1:
            msg = set(data["data"].split(","))
            chenels =[]
            for i in msg:
                if int(i) not in chanels and 0<int(i)<7:
                    chanels.append(int(i))
            chanels.sort()
            selected_chanels = {}
            for i in chanels:
                try:
                    selected_chanels[i] = reley_condition[i]
                except KeyError:
                    pass
            json_out["data"] = selected_chanels
            send_json(writer,json_out)

        elif "3" == command:
            if broadcasting == True:
                broadcasting = False
                writers_for_broadcast.remove(writer)
                json_out["data"] = "Broadcasting stoped"
                send_json(writer,json_out)
                print(f"{addr} removed from broadcast\n")

            elif broadcasting == False:
                broadcasting = True
                writers_for_broadcast.append(writer)
                json_out["data"] = "Broadcasting started"
                send_json(writer,json_out)
                print(f"{addr} added to broadcast\n")

        else:
            json_out["data"] = "Wrong command or not enough values"
            send_json(writer,json_out)

        await writer.drain()

        if data["command"] == "exit" or not data["command"]:
            print(f"{addr} disconnected")
            if broadcasting == True:
                writers_for_broadcast.remove(writer)
                print(f"{addr} removed from broadcast\n")
            break

    writer.close()

async def run_server() -> None:
    server = await asyncio.start_server(handler, "127.0.0.1", 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":

    observer = Observer()
    observer.schedule(MyEventHandler(), ".")
    observer.start()

    asyncio.run(run_server())

    observer.stop()
    observer.join()
