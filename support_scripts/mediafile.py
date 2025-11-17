from pymediainfo import MediaInfo
import requests
import re
import shutil
import logging
from pathlib import Path

class MediaFile():
    def __init__(self, watchpath: str, mediainfo: MediaInfo):
        self.watchpath = watchpath
        self.mediainfo = mediainfo

    def make_metadata(self):
        videocodec, width, height = self._get_videodata()
        self.item = self._get_item()
        self.filepath = self._get_filepath()
        self.mediatype = self._get_mediatype()
        self.wrapper = self.mediainfo.general_tracks[0].format
        self.videocodec = videocodec
        self.width = width
        self.height = height
        self.audiocodec = self._get_audiocodec()

        logging.info(f"metadata for '{self.watchpath}': {self.item}; {self.filepath}; {self.mediatype}; {self.wrapper}; {self.videocodec}; {self.audiocodec}; {self.width}; {self.height}")

    def _get_item(self) -> str:
        return re.match(r"([SVF]\d+)", self.mediainfo.general_tracks[0].file_name).group(1)
    
    def _get_filepath(self) -> str:
        return self.mediainfo.general_tracks[0].file_name_extension
    
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

    def push_mactaquac(self, apipath: str):
        data = {
            "item": self.item,
            "filepath": self.filepath,
            "type": self.mediatype,
            "wrapper": self.wrapper,
            "videocodec": self.videocodec if self.videocodec else "",
            "audiocodec": self.audiocodec if self.audiocodec else "",
            "width": self.width if self.width else "",
            "height": self.height if self.height else ""
        }            
        r = requests.post(apipath, data=data)

        if r.status_code == 201:
            logging.info(f"pushed data for '{self.watchpath}'")
        else:
            raise requests.ConnectionError(f"response code {r.status_code}")

    def move_media(self, mediafolder):
        dest = Path(mediafolder) / self.filepath
        shutil.copy(
            self.watchpath,
            dest
        )
        logging.info(f"copied '{self.watchpath}' to '{dest}'")

    @classmethod
    def from_path(cls, path:str) -> "MediaFile":
        return MediaFile(
            path,
            MediaInfo.parse(path)
        )

