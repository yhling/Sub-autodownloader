import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os.path as op
import PTN
from opensubtitlescom import OpenSubtitles

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

class opensub:
    def __init__(self, userName=None, password=None, apiKey=None, appName="Hoe") -> None:
        # Initialize the OpenSubtitles client
        self.subtitles = OpenSubtitles(apiKey, appName)

        # Log in (retrieve auth token)
        response = self.subtitles.login(userName, password)

    def download(self, filePath):
        mediaName = op.splitext(op.basename(filePath))[0]
        mediaDir = op.dirname(filePath)
        # Extract movie info from filename, if nothing found then extract from directory
        a = PTN.parse(mediaName)
        if 'year' not in a:
            dirName = op.basename(mediaDir)
            a = PTN.parse(dirName)
        if 'year' not in a:
            print("No info could be extracted from file or directory name.")
            return
        if op.exists(op.join(mediaDir, f"{mediaName}.srt")):
            print("Sub already exists for this file.")
            return
        # Search for subtitles
        print(f"Searching subtitle with title '{a['title']}' of year '{a['year']}'")
        response = self.subtitles.search(query=f"{a['title']}",  year=a["year"], type="movie", languages="en")
        self.change_download_dir(mediaDir)
        print(f"Downloading sub for '{filePath}'")
        self.subtitles.download_and_save(response.data[0], filename=f"{mediaName}.srt")
        print(f"Downloaded subtitle: '{mediaName}.srt'")

    def change_download_dir(self, dirPath):
        self.subtitles.downloads_dir = dirPath

config = generic_config(osub_user=None, osub_pass=None, osub_key=None, watch_pattern=["*.mkv", "*.mp4"])

if config.osub_user == None:
    config.osub_user = input("OpenSubtitles username: ")
    config.osub_pass = input("OpenSubtitles password: ")
    config.osub_key = input("OpenSubtitles API key (https://www.opensubtitles.com/en/consumers): ")
    config.commit()

subs = opensub(userName=config.osub_user, password=config.osub_pass, apiKey=config.osub_key)

patterns = config.watch_pattern
ignore_patterns = ["*.srt"]
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


def on_created(event):
    print(f"New file detected at '{event.src_path}'")
    try:  
        subs.download(event.src_path)
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