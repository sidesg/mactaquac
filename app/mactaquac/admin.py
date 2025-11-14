from django.contrib import admin

from .models import *

admin.site.register(Item)
admin.site.register(Wrapper)
admin.site.register(VideoCodec)
admin.site.register(AudioCodec)
admin.site.register(MediaFile)
