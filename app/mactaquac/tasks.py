import os
import logging
import time
import hashlib
import polars as pl

from celery import shared_task
from pathlib import Path
from contextlib import contextmanager
from django.core.cache import cache
from hashlib import md5

from .models import MediaFile, Wrapper, AudioCodec, VideoCodec, Item
from .mediafile import MediaFileBuilder

DOCKERMEDIA = os.getenv("DOCKERMEDIA")
LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes
DATAFILE = "data/SMI_allItems.csv"

@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        if time.monotonic() < timeout_at and status:
            cache.delete(lock_id)

@shared_task(bind=True, track_started=True)
def add_files(self):
    mediaroot_hexdigest = md5((DOCKERMEDIA).encode()).hexdigest()
    lock_id = '{0}-lock-{1}'.format(self.name, mediaroot_hexdigest)
    logging.info("Importing new files")
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            analyze_mediafolder(DOCKERMEDIA)
            logging.info("New file importing complete")
        else:
            logging.warning("Mactaquac is already importing new files")

def analyze_mediafolder(mediafolder: str):
    for child in Path(mediafolder).iterdir():
        if child.is_file():
            try:
                file = MediaFileBuilder.from_path(DOCKERMEDIA, child)
                file.make_metadata()
            except Exception as e:
                logging.warning(f"Unable to parse metadata for {child}: {e}")
                continue
            if MediaFile.objects.filter(filename=file.filename) or MediaFile.objects.filter(filepath=file.absolute_path):
                logging.debug(f"No import; {file.filename} already exists")
                continue
            else:
                try:
                    wrapper,_=Wrapper.objects.get_or_create(name=file.wrapper)
                    videocodec,_=VideoCodec.objects.get_or_create(name=file.videocodec)
                    audiocodec,_=AudioCodec.objects.get_or_create(name=file.audiocodec)
                    item,_=Item.objects.get_or_create(identifier=file.item)

                    MediaFile.objects.create(
                        item=item,
                        type=file.mediatype,
                        filename=file.filename,
                        filepath=file.filepath,
                        storage_location=file.storage_path,
                        wrapper=wrapper,
                        videocodec=videocodec,
                        audiocodec=audiocodec,
                        width=file.width,
                        height=file.height,
                        creation_date=file.creation_date,
                        filesize=file.size,
                        duration_min=file.minutes,
                        duration_sec=file.seconds
                    )
                    logging.info(f"Success; added {file.filename}")
                except Exception as e:
                    logging.warning(f"Unable to create entry for {file.filename}: {e}")
        elif child.is_dir():
            analyze_mediafolder(child)
        else:
            continue

@shared_task(bind=True, track_started=True)
def add_item_info(self):
    datafile_hexdigest = md5((DATAFILE).encode()).hexdigest()
    lock_id = '{0}-lock-{1}'.format(self.name, datafile_hexdigest)
    logging.info("Adding items")
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            if items:= Item.objects.filter(updated=False):
                df = pl.read_csv(
                    DATAFILE, 
                    encoding="windows-1252",
                    columns=["Identifier", "StrTitle", "Collection"]
                )
                for item in items:
                    try:
                        dff = df.filter(pl.col("Identifier") == item.identifier)
                        if len(dff) > 0:
                            title = dff.get_column('StrTitle')[0]
                            collection = dff.get_column('Collection')[0]

                            item.collection = collection
                            item.title = title if title else "[NO TITLE]"
                            item.updated = True
                            item.save()
                            logging.info(f"Updated {item.identifier}")
                        else:
                            logging.warning(f"No info for {item.identifier}")
                    except Exception as e:
                        logging.warning(f"Unable to update info for item {item.identifier}: {e}")
            else:
                logging.info("No items without info")
            logging.info("All new items added")
        else:
            logging.warning("Mactaquac is already adding new item info")

@shared_task(bind=True, track_started=True)
def add_checksums(self):
    mediaroot_hexdigest = md5((DOCKERMEDIA).encode()).hexdigest()
    lock_id = '{0}-lock-{1}'.format(self.name, mediaroot_hexdigest)
    logging.info("Generating checksums")
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            if files := MediaFile.objects.filter(checksum__isnull=True):
                for file in files:
                    try:
                        fullpath = Path(DOCKERMEDIA) / file.filepath
                        checksum = _make_checksum(fullpath)
                        file.checksum = checksum
                        file.save()
                    except Exception as e:
                        logging.warning(f"Unable to make checksum for {file.filename}: {e}")
            else:
                logging.info("No mediafiles without checksums")
            logging.debug("Checksums generated")
        else:
            logging.warning("Mactaquac is already generating checksums")

def _make_checksum(filepath) -> str:
    hash = hashlib.md5()
    with open(filepath, "rb") as file:
        while True:
            data = file.read(65536)
            if not data:
                break
            hash.update(data)
    return hash.hexdigest()

@shared_task(bind=True, track_started=True)
def prune_deleted(self):
    lock_id = '{0}-lock'.format(self.name)
    logging.info("Pruning deleted files from database")
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            mediaroot = Path(DOCKERMEDIA)
            if mediaroot.exists():
                for file in MediaFile.objects.all():
                    if not (mediaroot / file.filepath).exists():
                        storage_location = file.storage_location
                        file.delete()
                        logging.info(f"No file at {storage_location}; deleted entry")
                    else:
                        continue
            else:
                logging.warning("Unable to connect to media storage location; pruning aborted")
            logging.debug("Deleted files pruned")
        else:
            logging.warning("Mactaquac is already pruning deleted files")
