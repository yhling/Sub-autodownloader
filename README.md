# Sub-autodownloader
Watches a directory recursively for new files and download .srt for those newly detected files. Basically a standalone Bazaar.

# Demo
https://github.com/yhling/Sub-autodownloader/assets/9102395/736180ed-5da2-48ac-b866-fc1488a4b760

# Binaries
Currently only Windows binary is available. See [Releases](https://github.com/yhling/Sub-autodownloader/releases).

# Usage
On first run, it will prompt for opensubtitles username, password and consumer key. A consumer key can be generated at https://www.opensubtitles.com/en/consumers. You need an opensubtitles account.

By default, it watches for new `*.mp4` and `*.mkv` files. You can add more filename patterns in the `subconfig.json` file after running it the first time. 

# Make .exe
`python -m nuitka --onefile app.py`
