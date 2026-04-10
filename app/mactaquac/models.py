from django.db import models
from django.utils import timezone

class Item(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    title = models.CharField(default="[NONE]")
    collection = models.CharField(max_length=50, default="[NONE]")
    updated = models.BooleanField(default=False)

    def __str__(self):
        return self.identifier

class Wrapper(models.Model):
    name = models.CharField(max_length=255, unique=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class VideoCodec(models.Model):
    name = models.CharField(max_length=255, unique=True)
    notes = models.TextField(null=True, blank=True)

    @classmethod
    def get_default_pk(cls):
        codec, _ = cls.objects.get_or_create(
            name='No Image'
        )
        return codec.pk

    def __str__(self):
        return self.name

class AudioCodec(models.Model):
    name = models.CharField(max_length=255, unique=True)
    notes = models.TextField(null=True, blank=True)

    @classmethod
    def get_default_pk(cls):
        codec, _ = cls.objects.get_or_create(
            name='No Sound'
        )
        return codec.pk

    def __str__(self):
        return self.name

class MediaFile(models.Model):
    TYPES = {
        "audio": "audio",
        "video": "video",
        "textual": "textual"
    }
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="mediafiles")
    type = models.CharField(max_length=255, choices=TYPES)
    filename = models.CharField(unique=True)
    filepath = models.CharField(unique=True)
    storage_location = models.CharField()
    wrapper = models.ForeignKey(Wrapper, on_delete=models.SET_NULL, null=True, blank=True)
    videocodec = models.ForeignKey(VideoCodec, on_delete=models.SET_DEFAULT, default=VideoCodec.get_default_pk())
    audiocodec = models.ForeignKey(AudioCodec, on_delete=models.SET_DEFAULT, default=AudioCodec.get_default_pk())
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    checksum = models.CharField(null=True, blank=True)
    creation_date = models.DateField(null=True, blank=True)
    filesize = models.FloatField(default=0)
    duration_min = models.IntegerField(null=True, blank=True)
    duration_sec = models.IntegerField(null=True, blank=True)
    date_added = models.DateField(default=timezone.now())
    date_modified = models.DateField(null=True, blank=True)

    def find_duplicates(self):
        return MediaFile.objects.filter(checksum=self.checksum)

    def __str__(self):
        return self.filename
