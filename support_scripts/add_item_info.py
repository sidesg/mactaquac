import polars as pl
import requests
import logging
import os
from dotenv import load_dotenv
import datetime

DATAFILE = "../data/SMI_allItems.csv"
# LOGFOLDER = "../notes/logs"
load_dotenv("../.env")
LOGFOLDER = os.getenv("LOGFOLDER")

def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.DEBUG,
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

    s = requests.Session()
    items_to_mactaquac(
        "http://localhost/mactaquac/api/item/",
        df, s
    )

def items_to_mactaquac(endpoint: str, df: pl.DataFrame, session: requests.Session):
    r = session.get(endpoint)
    if r.status_code == 200:
        resultjson: dict = r.json()
        for item in resultjson["results"]:
            if item["updated"] == True:
                continue

            itemnumber = item["identifier"]
            dff = df.filter(pl.col("Identifier") == itemnumber)

            if len(dff) == 0:
                logging.warning(f"no catalogue info for {itemnumber}")
                continue

            try:
                r = requests.patch(
                    f"http://localhost/mactaquac/api/item/{itemnumber}/",
                    data={
                        "collection": dff.get_column('Collection')[0],
                        "title": dff.get_column('StrTitle')[0],
                        "updated": "True"
                    }
                )

                if r.status_code == 200:
                    logging.info(f"updated {itemnumber}")
                else:
                    logging.warning(f"error processing {itemnumber}, status {r.status_code}: {r.reason}")
            except Exception as e:
                logging.warning(f"error in api call for {itemnumber}: {e}")
        
        if nextpage := resultjson.get("next", None):
            items_to_mactaquac(nextpage, df, session)
    else:
        logging.warning(f"error in api call to {endpoint}: response code {r.status_code}")

if __name__ == "__main__":
    main()
