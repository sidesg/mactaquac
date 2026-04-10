import os
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
from mediafile import MediaFile
import requests

load_dotenv("../.env")
MEDIAROOT = os.getenv("MEDIAFOLDER")
LOGFOLDER = os.getenv("LOGFOLDER")
TOKEN = "7d6fbda800a8525c93d868d76bdbd1699be37fab"

def main():
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

    with requests.Session() as s:
        s.headers.update({"Token": TOKEN})
        analyze_mediafolder(MEDIAROOT, s)

def analyze_mediafolder(mediafolder: str, session: requests.Session):
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
                    "http://localhost/mactaquac/api/mediafile/"
                )
            except Exception as e:
                logging.warning(f"unable to push data for '{child}': {e}")
                continue

        elif child.is_dir():
            analyze_mediafolder(child, session)
        else:
            continue


if __name__ == "__main__":
    main()
