from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

with open("f.txt", "r") as f:
    to_out = f.readlines()
    f.close()
fname = "f.txt"
# class MyEventHandler(FileSystemEventHandler):
#     def on_closed(self, event):
#         global to_out
#         if event.src_path == './f.txt':
#             with open("f.txt", "r") as f:
#                 try:
#
#                     conditions = f.readline().strip("\n").split(" ")[:6]
#                     for i in reley_condition:
#                         reley_condition[i] = conditions[i - 1]
#
#                     status_broadcast(json.dumps(reley_condition))
#
#                     print(f"Conditions change by reley:\n{json.dumps(reley_condition, indent=2)}")
#
#                 except IndexError:
#                     print("Error: Not enough values from reley file")
#                     exit(0)

# class MyEventHandler(FileSystemEventHandler):
#     def on_any_event(self, event):
#         global to_out
#         if event.src_path=='./f.txt':
#             with open("f.txt","r") as f:
#                 to_out=f.readlines()
#                 f.close()
#             print(event)
#             print(to_out)
class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        global to_out
        if event.src_path=='./f.txt':
            with open("f.txt","r") as f:
                to_out=f.readlines()
                f.close()
            print(event)
            print(to_out)

observer = Observer()
observer.schedule(MyEventHandler(), ".")#, recursive=True)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
observer.join()
