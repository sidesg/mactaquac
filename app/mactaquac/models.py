from django.db import models

class Item(models.Model):
    identifier = models.CharField(max_length=255, unique=True)

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

    def __str__(self):
        return self.name

class AudioCodec(models.Model):
    name = models.CharField(max_length=255, unique=True)
    notes = models.TextField(null=True, blank=True)

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
    filepath = models.CharField(unique=True)
    wrapper = models.ForeignKey(Wrapper, on_delete=models.SET_NULL, null=True, blank=True)
    videocodec = models.ForeignKey(VideoCodec, on_delete=models.SET_NULL, null=True, blank=True)
    audiocodec = models.ForeignKey(AudioCodec, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.filepath
