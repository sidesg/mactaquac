from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response

from .models import MediaFile, Item
from .serializers import MediaFileSerializer, ItemSerializer


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class MediaFileViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    queryset = MediaFile.objects.all()

class ItemViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
