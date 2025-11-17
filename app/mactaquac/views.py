from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from rest_framework import viewsets
from rest_framework.response import Response

from .models import MediaFile, Item
from .serializers import MediaFileSerializer, ItemSerializer

import mimetypes
from pathlib import Path

MEDIA_ROOT = "/app/media"

def index(request):
    return HttpResponse("Hello, world. You're at the Mactaquac index.")

class MediaFileViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    queryset = MediaFile.objects.all()

class ItemViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()

def download_media(request, filename):
    safe_path: Path = Path(MEDIA_ROOT) / filename
    if not str(safe_path).startswith(MEDIA_ROOT):
        raise Http404("Invalid file path.")

    if not safe_path.exists():
        raise Http404("File not found.")

    mime_type, _ = mimetypes.guess_type(safe_path)

    return FileResponse(
        open(safe_path, "rb"),
        as_attachment=True,
        filename=filename,
        content_type=mime_type or "application/octet-stream",
    )
