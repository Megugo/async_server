from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

with open("f.txt", "r") as f:
    to_out = f.readlines()
    f.close()
fname = "f.txt"

class MyEventHandler(FileSystemEventHandler):
    def on_closed(self, event):#on_modified(self, event):
        global to_out
        if event.src_path=='./f.txt':
            with open("f.txt","r") as f:
                to_out=f.readlines()
                f.close()
            print(event)
            print(to_out)
        #print(f'Got event: {event}')


observer = Observer()
observer.schedule(MyEventHandler(), ".")#, recursive=True)
observer.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()
observer.join()