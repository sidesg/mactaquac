import requests
import logging
import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv("../.env")
LOGFOLDER = os.getenv("LOGFOLDER")
MEDIAROOT = os.getenv("MEDIAFOLDER")
ENDPOINT = "http://localhost/mactaquac/api/mediafile/"

def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M",
        filename=f"{LOGFOLDER}/fileprune-{now}.log",
        encoding="utf-8",
        filemode="a",
    )
    session = requests.Session()
    for fileurl, storage_location in mediafile_generator(ENDPOINT, session):
        if not Path(storage_location).exists():
            try:
                r = session.delete(fileurl)
                if r.status_code == 204:
                    logging.info(f"no file at {storage_location}; deleted {fileurl}")
                else:
                    logging.warning(f"no file at {storage_location}; unable to delete {fileurl};status code {r.status_code}")
            except Exception as e:
                logging.warning(f"no file at {storage_location}; unable to delete {fileurl}; {e}")

def mediafile_generator(endpoint: str, session: requests.Session):
    try:
        r = session.get(endpoint)
        if r.status_code == 200:
            resultjson: dict = r.json()

            jsonmediafiles = [
                file for file
                in resultjson["results"]
            ]

            for jsonmediafile in jsonmediafiles:
                fileurl = ENDPOINT + str(jsonmediafile["id"]) +"/"
                storage_location = jsonmediafile["storage_location"]
                yield fileurl, storage_location

            if nextpage := resultjson["next"]:
                for fileurl, storage_location in mediafile_generator(nextpage, session):
                    yield fileurl, storage_location
    except Exception as e:
        logging.warning(f"error in api call to {endpoint}: {e}")

if __name__ == "__main__":
    main()