import os
import re
import shutil
import logging
import hashlib
import datetime
from pathlib import Path
from pymediainfo import MediaInfo

DOCKERMEDIA = os.getenv("DOCKERMEDIA")
MOUNTED_STORAGE = os.getenv("MEDIAFOLDER")

class MediaFileBuilder():
    def __init__(self, watchfolder: str, absolute_path: str):
        self.watchfolder = watchfolder
        self.absolute_path = absolute_path

    def make_metadata(self):
        self.filename = Path(self.absolute_path).name
        self.item = self._get_item()
        self.mediainfo = self._make_mediainfo()
        self.mediatype = self._get_mediatype()

        videocodec, width, height = self._get_videodata()
        duration_mins, duration_secs = self._get_duration()
        filepath, storage_path = self._make_paths()

        self.filepath = filepath
        self.storage_path = storage_path
        self.wrapper = self.mediainfo.general_tracks[0].format
        self.videocodec = videocodec
        self.width = width
        self.height = height
        self.audiocodec = self._get_audiocodec()
        self.creation_date = self._get_creation_date()
        self.size = self._get_size()
        self.minutes = duration_mins
        self.seconds = duration_secs
        self.date_added = datetime.date.today().strftime("%Y-%m-%d")

    def _make_paths(self):
        filepath = Path(self.absolute_path).relative_to(self.watchfolder)
        storage = Path(MOUNTED_STORAGE) / filepath
        return filepath, storage

    # def _make_storage_location(self):
    #     # storage = Path(self.absolute_path).relative_to(DOCKERMEDIA)
    #     storage = Path(MOUNTED_STORAGE) / self.filepath
    #     return storage

    def _get_item(self) -> str:
        if match := re.match(r"([SVF])(\d+[A-G]?)", self.filename):
            prefix = match.group(1)
            number = match.group(2)
            number = number.zfill(5)
            return prefix + number
        elif match := re.match(r"(SCD)(\d+[A-G]?)", self.filename):
            prefix = match.group(1)
            number = match.group(2)
            number = number.zfill(5)
            return "S" + number
        else:
            raise RuntimeError("unable to parse item number")
        
    def _make_mediainfo(self):
        try:
            return MediaInfo.parse(self.absolute_path)
        except:
            raise RuntimeError("mediainfo cannot parse file")

    # def _get_filepath(self) -> str:
    #     filepath = Path(self.absolute_path).relative_to(self.watchfolder)
    #     return filepath
    
    def _get_mediatype(self) -> str:
        if self.mediainfo.video_tracks:
            return "video"
        elif self.mediainfo.audio_tracks:
            return "audio"
        else:
            # return "textual"
            raise RuntimeError("no parsable video or audio streams")
    
    def _get_videodata(self):
        if videotracks := self.mediainfo.video_tracks:
            return videotracks[0].format, videotracks[0].width, videotracks[0].height
        else:
            return "No Image", None, None
    
    def _get_audiocodec(self):
        if audiotracks := self.mediainfo.audio_tracks:
            return audiotracks[0].format
        else:
            return "No Sound"

    def _get_creation_date(self):
        if datetime := self.mediainfo.general_tracks[0].encoded_date:
            match = re.match(r"(\d{4}-\d{2}-\d{2})", datetime).group(1)
            return match if match else None
        else:
            return None

    def _get_size(self):
        bytes = self.mediainfo.general_tracks[0].file_size
        return round(bytes / (1024 * 1024), 2)

    def _get_duration(self):
        try:
            m, s = divmod(self.mediainfo.general_tracks[0].duration, 60000)
            return m, round(s / 1000, 0)
        except:
            return 0, 0

    def _make_checksum(self) -> str:
        hash = hashlib.md5()
        fullpath = Path(self.absolute_path).relative_to(MOUNTED_STORAGE)
        fullpath = Path(DOCKERMEDIA)/ fullpath
        with open(fullpath, "rb") as file:
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
    def from_path(cls, watchfolder: str, absolute_path:str) -> "MediaFileBuilder":
        return MediaFileBuilder(
            watchfolder,
            absolute_path,
        )
