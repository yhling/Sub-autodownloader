import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os.path as op
import PTN
import json
from opensubtitles_api import OpenSubtitlesAPI

class generic_config:
    def __init__(self, **kwargs):
        import json
        from types import SimpleNamespace
        self.configNames = kwargs
        try:
            with open('subconfig.json') as f:
                c = json.load(f)
            for i in kwargs:
                c[i]
            self.configItems = SimpleNamespace(**c)
        except:
            self.configItems = SimpleNamespace(**kwargs)
        self.__dict__.update(self.configItems.__dict__)

    def __setattr__(self, __name, __value):
        super(generic_config, self).__setattr__(__name, __value)
        if __name in self.configNames:
            self.configItems.__dict__[__name] = __value

    def commit(self):
        import json
        with open('subconfig.json', 'w') as f:
            json.dump(self.configItems.__dict__, f)


config = generic_config(osub_user=None, osub_pass=None, osub_key=None, watch_pattern=["*.mkv", "*.mp4"])

if config.osub_user == None:
    config.osub_user = input("OpenSubtitles username: ")
    config.osub_pass = input("OpenSubtitles password: ")
    config.osub_key = input("OpenSubtitles API key (https://www.opensubtitles.com/en/consumers): ")
    config.commit()

subs = OpenSubtitlesAPI(userName=config.osub_user, password=config.osub_pass, apiKey=config.osub_key)

patterns = config.watch_pattern
ignore_patterns = ["*.srt"]
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


def on_created(event):
    print(f"New file detected at '{event.src_path}'")
    try:  
        subs.download_subtitle(event.src_path)
    except Exception as e:
        print(e)

def on_deleted(event):
    pass
    #print(f"what the f**k! Someone deleted {event.src_path}!")

def on_modified(event):
    pass
    #print(f"hey buddy, {event.src_path} has been modified")

def on_moved(event):
    pass
    #print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

path = input("Enter directory path to monitor: ")
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

print(f"Watching the directory '{path}' for new files...")
my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()