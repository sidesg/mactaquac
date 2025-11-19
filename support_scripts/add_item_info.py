import polars as pl
import requests
import logging
from dotenv import load_dotenv
import datetime

DATAFILE = "../data/SMI_allItems.csv"
LOGFOLDER = "../notes/logs"
load_dotenv("../.env")

def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M",
        filename=f"{LOGFOLDER}/itemupdate-{now}.log",
        encoding="utf-8",
        filemode="a",
    )
    df = pl.read_csv(
        DATAFILE, 
        encoding="windows-1252",
        columns=["Identifier", "StrTitle", "Collection"]
    )

    unupdated = get_unupdated()

    for itemnumber in unupdated:
        dff = df.filter(pl.col("Identifier") == itemnumber)

        if len(dff) == 0:
            logging.warning(f"no catalogue info for {itemnumber}")
            continue

        try:
            r = requests.patch(
                f"http://localhost:8000/mactaquac/api/item/{itemnumber}/",
                data={
                    "collection": dff.get_column('Collection')[0],
                    "title": dff.get_column('StrTitle')[0],
                    "updated": "True"
                }
            )
            print(r.url)
            if r.status_code == 200:
                logging.info(f"updated {itemnumber}")
            else:
                logging.warning(f"error processing {itemnumber}, status {r.status_code}")
        except Exception as e:
            logging.warning(f"error in api call for {itemnumber}: {e}")


def get_unupdated() -> list:
    r = requests.get(
        "http://localhost:8000/mactaquac/api/item/?updated=False"
    )

    if r.status_code == 200:
        return [
            item["identifier"]
            for item in r.json()
        ]
    else:
        return []


if __name__ == "__main__":
    main()
