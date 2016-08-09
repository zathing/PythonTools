#!/usr/bin/env python
#coding=utf-8

import os,datetime
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE,IN_MODIFY
wm = WatchManager()
mask = IN_DELETE | IN_CREATE |IN_MODIFY

class PFilePath(ProcessEvent):
    def process_IN_CREATE(self, event):
        print  "%s Create file: %s " %  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),os.path.join(event.path, event.name))
    def process_IN_DELETE(self, event):
        print  "%s Delete file: %s " %  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),os.path.join(event.path, event.name))
    def process_IN_MODIFY(self, event):
        print  "%s Modify file: %s " %  (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),os.path.join(event.path, event.name))
        
if __name__ == "__main__":
    notifier = Notifier(wm, PFilePath())
    wdd = wm.add_watch('.', mask, rec=True)
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:   
            notifier.stop()
            break
