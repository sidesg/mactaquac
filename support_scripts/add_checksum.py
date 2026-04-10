from mediafile import MediaFile
import requests
import logging
import datetime
from dotenv import load_dotenv
import os

load_dotenv("../.env")
LOGFOLDER = os.getenv("LOGFOLDER")
MEDIAROOT = os.getenv("MEDIAFOLDER")
ENDPOINT = "http://localhost/mactaquac/api/mediafile/"
TOKEN = "7d6fbda800a8525c93d868d76bdbd1699be37fab"

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

    with requests.Session() as s:
        s.headers.update({"Token": TOKEN})
        process_items(ENDPOINT, s)

def process_items(endpoint: str, session: requests.Session):
    try:
        r = session.get(endpoint)
        if r.status_code == 200:
            resultjson: dict = r.json()

            jsonmediafiles = [
                file for file
                in resultjson["results"]
            ]

            for jsonmediafile in jsonmediafiles:
                mediafile = MediaFile.from_path(
                    MEDIAROOT,
                    jsonmediafile["storage_location"]
                )
                if jsonmediafile["checksum"]:
                    continue

                mediafilenumber=jsonmediafile["id"]  
                filename = jsonmediafile["filename"]
                absolutepath = jsonmediafile["storage_location"]

                try:
                    checksum = mediafile._make_checksum()
                except Exception as e:
                    logging.warning(f"unable to produce checksum for {absolutepath}")
                    continue

                
                try:
                    r = requests.patch(
                        f"{ENDPOINT}{mediafilenumber}/",
                        data={
                            "checksum": checksum,
                            "date_modified": datetime.date.today().strftime("%Y-%m-%d"),
                        },
                        headers={"Token": TOKEN}
                    )
                    if r.status_code == 200:
                        logging.info(f"updated {filename}")
                    else:
                        raise requests.ConnectionError(f"{r.status_code}: {r.reason}")
                except Exception as e:
                    logging.warning(f"error in api call for {filename}: {e}")

            if nextpage := resultjson["next"]:
                process_items(nextpage, session)
    except Exception as e:
        logging.warning(f"error in api call to {endpoint}: {e}")

if __name__ == "__main__":
    main()
