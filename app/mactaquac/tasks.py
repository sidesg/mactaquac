import os
import logging
import time

from celery import shared_task
from pathlib import Path
from contextlib import contextmanager
from django.core.cache import cache
from hashlib import md5

from .models import MediaFile, Wrapper, AudioCodec, VideoCodec, Item
from .mediafile import MediaFileBuilder

DOCKERMEDIA = os.getenv("DOCKERMEDIA")
LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes

@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)

@shared_task(bind=True, track_started=True)
def add_files(self):
    # The cache key consists of the task name and the MD5 digest
    # of the media root.
    mediaroot_hexdigest = md5((DOCKERMEDIA).encode()).hexdigest()
    lock_id = '{0}-lock-{1}'.format(self.name, mediaroot_hexdigest)
    logging.debug("Importing new files")
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            analyze_mediafolder(DOCKERMEDIA)
    logging.warning("Mactaquac is already importing new files")

def analyze_mediafolder(mediafolder: str):
    for child in Path(mediafolder).iterdir():
        if child.is_file():
            try:
                file = MediaFileBuilder.from_path(DOCKERMEDIA, child)
                file.make_metadata()
            except Exception as e:
                logging.warning(f"unable to parse metadata for {child}: {e}")
                continue
            if MediaFile.objects.filter(filename=file.filename) or MediaFile.objects.filter(filepath=file.absolute_path):
                logging.debug(f"no import; {file.filename} already exists")
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
                    logging.info(f"success; added {file.filename}")
                except Exception as e:
                    logging.warning(f"unable to create entry for {file.filename}: {e}")
        elif child.is_dir():
            analyze_mediafolder(child)
        else:
            continue
