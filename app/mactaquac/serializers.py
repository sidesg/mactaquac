from rest_framework import serializers
from .models import *

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["identifier", "title", "collection", "updated"]

class MediaFileSerializer(serializers.ModelSerializer):
    item = serializers.CharField()
    wrapper = serializers.CharField()
    videocodec = serializers.CharField(allow_blank=True, required=False)
    audiocodec = serializers.CharField(allow_blank=True, required=False)
    checksum = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data: dict):
        item_data = validated_data.pop('item')
        wrapper_data = validated_data.pop('wrapper')
        videocodec_data = validated_data.pop('videocodec', None)
        audiocodec_data = validated_data.pop('audiocodec', None)

        payload_item, _ = Item.objects.get_or_create(identifier=item_data)
        payload_wrapper, _ = Wrapper.objects.get_or_create(name=wrapper_data)
        if videocodec_data:
            payload_videocodec, _ = VideoCodec.objects.get_or_create(name=videocodec_data)
        else:
            payload_videocodec = None
        if audiocodec_data:
            payload_audiocodec, _ = AudioCodec.objects.get_or_create(name=audiocodec_data)
        else:
            payload_audiocodec=None

        mediafile = MediaFile.objects.create(
            item=payload_item,
            wrapper=payload_wrapper,
            videocodec=payload_videocodec,
            audiocodec=payload_audiocodec,
            **validated_data
        )

        return mediafile
    
    class Meta:
        model = MediaFile
        fields = "__all__"
