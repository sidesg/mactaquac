from rest_framework import serializers
from .models import *

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["identifier"]

class WrapperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wrapper
        fields = ["name"]

class VideoCodecSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCodec
        fields = ["name"]

class AudioCodecSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioCodec
        fields = ["name"]

class MediaFileSerializer(serializers.ModelSerializer):
    item = serializers.CharField()
    wrapper = serializers.CharField()
    videocodec = serializers.CharField(allow_blank=True, required=False)
    audiocodec = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        item_data = validated_data.pop('item')
        wrapper_data = validated_data.pop('wrapper')
        videocodec_data = validated_data.pop('videocodec')
        audiocodec_data = validated_data.pop('audiocodec')

        payload_item, _ = Item.objects.get_or_create(identifier=item_data)
        payload_wrapper, _ = Wrapper.objects.get_or_create(name=wrapper_data)
        payload_videocodec, _ = VideoCodec.objects.get_or_create(name=videocodec_data)
        payload_audiocodec, _ = AudioCodec.objects.get_or_create(name=audiocodec_data)

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
        fields = ["pk", "item", "type", "filepath", "wrapper", "videocodec", "audiocodec", "width", "height"]
