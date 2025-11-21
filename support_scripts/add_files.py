import os
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from mediafile import MediaFile
import requests
import asyncio
import re

load_dotenv("../.env")
MEDIAROOT = os.getenv("MEDIAFOLDER")
LOGFOLDER = os.getenv("LOGFOLDER")
WORKERS = 4

async def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M",
        filename=f"{LOGFOLDER}/ingest-{now}.log",
        encoding="utf-8",
        filemode="a",
    )
    
    work_queue = asyncio.Queue()
    pathlist = list()

    get_mediafilepaths(MEDIAROOT, pathlist)

    workers = {
        asyncio.Task(worker((idx+1), LOGFOLDER, work_queue))
        for idx in range(WORKERS)
    }

def get_mediafilepaths(mediafolder: str, pathlist: list):
    for child in Path(mediafolder).iterdir():
        if child.is_file():
            if re.search(r"[SVF]") and child.suffix in ["mov", "mp3"]:
                pathlist.append(child.absolute())
        elif child.is_dir():
            get_mediafilepaths(child, pathlist)
        else:
            continue

async def worker(name, logpath, work_queue: asyncio.Queue):
    while True:
        try:
            filepath: str = await work_queue.get()
        except Exception as e:
            work_queue.task_done()

def analyze_mediafolder(mediafolder: str):
    s = requests.Session()
    for child in Path(mediafolder).iterdir():
        if child.is_file():
            try:
                file = MediaFile.from_path(MEDIAROOT, child)
                file.make_metadata()
            except Exception as e:
                logging.warning(f"unable to parse metadata for {child}: {e}")
                continue
            try:
                file.push_mactaquac(
                    "http://localhost:8000/mactaquac/api/mediafile/", s)
            except Exception as e:
                logging.warning(f"unable to push data for {child}: {e}")
                continue

        elif child.is_dir():
            analyze_mediafolder(child)
        else:
            continue


if __name__ == "__main__":
    main()
