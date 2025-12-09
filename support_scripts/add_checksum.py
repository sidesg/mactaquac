from mediafile import MediaFile
import requests
import logging
import datetime
from dotenv import load_dotenv
import os

load_dotenv("../.env")
LOGFOLDER = os.getenv("LOGFOLDER")
ENDPOINT = "http://localhost/mactaquac/api/mediafile/"

def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M",
        filename=f"{LOGFOLDER}/checksum-{now}.log",
        encoding="utf-8",
        filemode="a",
    )

    s = requests.Session()



def process_items(endpoint: str, session: requests.Session):
    r = session.get(ENDPOINT)
    if r.status_code == 200:
        resultjson: dict = r.json()

        jsonmediafiles = [
            file for file
            in resultjson["results"]
        ]

        for jsonmediafile in jsonmediafiles:
            ...
            # make checksum and add to mactaquac

        if nextpage := resultjson["next"]:
            process_items(nextpage, session)