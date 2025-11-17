import logging
import datetime
from pathlib import Path
from mediafile import MediaFile

WATCHFOLDER = "/mnt/hdd1/mactaquac_dev/to_ingest"
MEDIAFOLDER = "/mnt/hdd1/mactaquac_dev/media"
REPORTFOLDER = "../notes"
LOGFOLDER = "../notes/logs"

def main():
    now = datetime.datetime.now().strftime("%Y%m%d")
    logging.basicConfig(
        format="{asctime} {levelname} {name} {message}",
        style="{",
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M",
        filename=f"{LOGFOLDER}/ingest-{now}.log",
        encoding="utf-8",
        filemode="a",
    )

    analyze_watchfolder(WATCHFOLDER)

def analyze_watchfolder(watchfolder: str):
    for child in Path(watchfolder).iterdir():
        if child.is_file():
            try:
                file = MediaFile.from_path(child)
                file.make_metadata()
            except Exception as e:
                logging.warning(f"unable to parse metadata for {child}: {e}")
                continue
            
            try:
                file.move_media(MEDIAFOLDER)
            except Exception as e:
                logging.warning(f"unable to move file {child}: {e}")
                continue
            
            try:
                file.push_mactaquac("http://localhost:8000/mactaquac/api/mediafile/")
            except Exception as e:
                logging.warning(f"unable to push data for {child}: {e}")
                # delete MEDIAFOLDER copy
                continue
            else:
                # Delete WATCHFOLDER copy
                ...

        elif child.is_dir():
            analyze_watchfolder(child)
        else:
            pass


if __name__ == "__main__":
    main()
