from pymediainfo import MediaInfo
import requests
import re
import shutil
import logging
import hashlib
from pathlib import Path

class MediaFile():
    def __init__(self, watchfolder: str, mediapath: str, mediainfo: MediaInfo):
        self.watchfolder = watchfolder
        self.mediapath = mediapath
        self.mediainfo = mediainfo

    def make_metadata(self):
        videocodec, width, height = self._get_videodata()
        duration_mins, duration_secs = self._get_duration()

        self.item = self._get_item()
        self.filename = self.mediainfo.general_tracks[0].file_name_extension
        self.filepath = self._get_filepath()
        self.mediatype = self._get_mediatype()
        self.wrapper = self.mediainfo.general_tracks[0].format
        self.videocodec = videocodec
        self.width = width
        self.height = height
        self.audiocodec = self._get_audiocodec()
        self.creation_date = self._get_creation_date()
        self.size = self._get_size()
        self.minutes = duration_mins
        self.seconds = duration_secs


        logging.info(f"metadata for '{self.mediapath}': {self.item}; {self.filepath}; {self.mediatype}; {self.wrapper}; {self.videocodec}; {self.audiocodec}; {self.width}; {self.height}")

    def _get_item(self) -> str:
        match = re.match(r"([SVF])(\d+)", self.mediainfo.general_tracks[0].file_name)
        prefix = match.group(1)
        number = match.group(2)
        number = number.zfill(5)
        return prefix + number
    
    def _get_filepath(self) -> str:
        filepath = Path(self.mediapath).relative_to(self.watchfolder)
        return filepath
    
    def _get_mediatype(self) -> str:
        if self.mediainfo.video_tracks:
            return "video"
        elif self.mediainfo.audio_tracks:
            return "audio"
        else:
            return "textual"
    
    def _get_videodata(self):
        if videotracks := self.mediainfo.video_tracks:
            return videotracks[0].format, videotracks[0].width, videotracks[0].height
        else:
            return None, None, None
    
    def _get_audiocodec(self):
        if audiotracks := self.mediainfo.audio_tracks:
            return audiotracks[0].format
        else:
            return None

    def _get_creation_date(self):
        datetime = self.mediainfo.general_tracks[0].encoded_date
        match = re.match(r"(\d{4}-\d{2}-\d{2})", datetime).group(1)
        return match if match else None

    def _get_size(self):
        bytes = self.mediainfo.general_tracks[0].file_size
        return round(bytes / (1024 * 1024), 2)

    def _get_duration(self):
        m, s = divmod(self.mediainfo.general_tracks[0].duration, 60000)
        return m, round(s / 1000, 0)

    def push_mactaquac(self, apipath: str):
        data = {
            "item": self.item,
            "filename": self.filename,
            "filepath": self.filepath,
            "storage_location": self.mediapath,
            "type": self.mediatype,
            "wrapper": self.wrapper,
            "videocodec": self.videocodec if self.videocodec else "No image",
            "audiocodec": self.audiocodec if self.audiocodec else "No sound",
            "width": self.width if self.width else "",
            "height": self.height if self.height else "",
            "checksum": self._make_checksum(),
            "filesize": self.size,
            "duration_min": self.minutes,
            "duration_sec": self.seconds,
            "creation_date": self.creation_date
        }            
        r = requests.post(apipath, data=data)

        if r.status_code == 201:
            logging.info(f"pushed data for '{self.mediapath}'")
        else:
            raise requests.ConnectionError(f"response code {r.status_code}")

    def _make_checksum(self) -> str:
        hash = hashlib.md5()
        with open(self.mediapath, "rb") as file:
            while True:
                data = file.read(65536)
                if not data:
                    break
                hash.update(data)
    
        return hash.hexdigest()

    def move_media(self, mediafolder):
        dest = Path(mediafolder) / self.filepath
        shutil.copy(
            self.watchpath,
            dest
        )
        logging.info(f"copied '{self.watchpath}' to '{dest}'")

    @classmethod
    def from_path(cls, watchfolder: str, path:str) -> "MediaFile":
        return MediaFile(
            watchfolder,
            path,
            MediaInfo.parse(path)
        )

