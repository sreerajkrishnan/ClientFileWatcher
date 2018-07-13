#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import DataAnchor
import sys

class OnCreationHandler(FileSystemEventHandler):
    def on_created(self, event):
        if( not event.src_path.endswith('.enc')):
            DataAnchor.encryptFile(event.src_path)
            print 'done'
        return

if __name__ == "__main__":
    event_handler = OnCreationHandler()
    observer = Observer()
    observer.schedule(event_handler, path=sys.argv[1], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()