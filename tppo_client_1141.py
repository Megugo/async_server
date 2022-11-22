import asyncio
import json
def info_message():
    print("Commands:\n 1 - переключает заданные каналы,\n формат записи '1 {chanel_number:condition}', condition = [0,1]\n")
    print(" 2 - получает состояние заданных каналов,\n формат '2 chanel_number_1,chanel_number_2...'\n")
    print(" 3 - включает режим отслеживания обновлений состояния реле,\n формат '3', CTRL+C отключает режим отслеживания\n")
    print(" info - для получения информации по командам\n")
    print(" exit - выход из приложения\n")

def send_json(writer,json_dict):
    writer.write(json.dumps(json_dict).encode())

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    info_message()

    while True:
        message = input()

        if message == 'info':
            info_message()
            continue

        splited_message = message.split(" ")[:2]

        if splited_message[0] in ["1","2"] and len(splited_message)>1:
            json_message = {"command":splited_message[0],"data":splited_message[1]}

        elif splited_message[0] in ['3',"exit"]:
            json_message = {"command":splited_message[0],"data":""}

        else:
            print("Wrong command or not enough values")
            continue

        if message:
            print(f'Send: {json.dumps(json_message, indent=2)}')
            send_json(writer,json_message)

        if splited_message[0]== '3':
            while True:
                try:
                    data = await reader.read(1000)
                    if data!=b"":
                        print(f'Received: {json.loads(data.decode())["data"]}')

                except BaseException:#KeyboardInterrupt:
                    print("closing")
                    send_json(writer,{"command":"3","data":""})
                    break

        await writer.drain()
        data = await reader.read(1000)

        if message == "exit":
            print("exit")
            break
        if data!=b"":
            print(data.decode())
            print(f'Conditions changed: {json.loads(data.decode())["data"]}')

    print('Close the connection')

    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client())
