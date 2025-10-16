import os.path as op
import requests


class OpenSubtitlesAPI:
    def __init__(self, userName=None, password=None, apiKey=None, appName="SubDownloader") -> None:
        self.base_url = "https://api.opensubtitles.com/api/v1"
        self.api_key = apiKey
        self.app_name = appName
        self.token = None
        self.downloads_dir = "."
        
        # Log in (retrieve auth token)
        if userName and password:
            self.login(userName, password)

    def login(self, username, password):
        """Authenticate with OpenSubtitles API"""
        url = f"{self.base_url}/login"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{self.app_name} v1.0",
            "Api-Key": self.api_key
        }
        
        data = {
            "username": username,
            "password": password
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.token = result.get("token")
            print("Successfully authenticated with OpenSubtitles API")
            return result
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            raise

    def search(self, query, year=None, release=None, languages="en"):
        """Search for subtitles"""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
            
        url = f"{self.base_url}/subtitles"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Api-Key": self.api_key,
            "User-Agent": f"{self.app_name} v1.0"
        }
        
        params = {
            "languages": languages
        }
        
        if year:
            params["year"] = year
        if release and release != "":
            params["query"] = f"{query} {release}"
        else:
            params["query"] = query
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print(f"Search failed: {e}")
            print(f"Response: {response.text}")
            raise

    def download(self, file_id, filename):
        """Download subtitle file"""
        if not self.token:
            raise Exception("Not authenticated. Please login first.")
            
        # First, get download URL
        url = f"{self.base_url}/download"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Api-Key": self.api_key,
            "User-Agent": f"{self.app_name} v1.0",
            "Content-Type": "application/json"
        }
        
        data = {
            "file_id": file_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            download_url = result.get("link")
            
            if not download_url:
                raise Exception("No download URL received")
            
            # Download the actual file
            file_response = requests.get(download_url)
            file_response.raise_for_status()
            
            # Save to file
            filepath = op.join(self.downloads_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(file_response.content)
                
            print(f"Downloaded subtitle: '{filename}'")
            return filepath
            
        except requests.exceptions.RequestException as e:
            print(f"Download failed: {e}")
            raise

    def download_subtitle(self, filePath):
        """Main method to download subtitle for a video file"""
        import PTN
        
        mediaName = op.splitext(op.basename(filePath))[0]
        mediaDir = op.dirname(filePath)
        
        # Extract movie info from filename, if nothing found then extract from directory
        a = PTN.parse(mediaName, standardise=False)
        if 'year' not in a:
            dirName = op.basename(mediaDir)
            a = PTN.parse(dirName)
        if 'year' not in a:
            print("Year of release could not be determined from file or directory name.")
            a['year'] = None
        if 'quality' not in a:
            a['quality'] = None
        if op.exists(op.join(mediaDir, f"{mediaName}.srt")):
            print("Sub already exists for this file.")
            return
            
        # Search for subtitles
        print(f"Searching subtitle with title '{a['title']}' of year '{a['year']}' of release 'a['quality']'")
        search_result = self.search(query=a['title'], year=a['year'], release=a['quality'], languages="en")
        
        if not search_result.get('data') or len(search_result['data']) == 0:
            print("No subtitles found.")
            return
            
        # Change download directory
        self.change_download_dir(mediaDir)
        
        # Download the first result
        print(f"Downloading sub for '{filePath}'")
        subtitle_data = search_result['data'][0]
        print(f"Subtitle release name: {subtitle_data['attributes']['release']}")
        file_id = subtitle_data['attributes']['files'][0]['file_id']
        
        self.download(file_id, f"{mediaName}.srt")
        print(f"Downloaded subtitle: '{mediaName}.srt'")

    def change_download_dir(self, dirPath):
        """Set the download directory"""
        self.downloads_dir = dirPath
