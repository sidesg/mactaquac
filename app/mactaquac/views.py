from django.shortcuts import render
from django.http import HttpResponse, FileResponse, Http404
from django.views import generic

from rest_framework import viewsets
from rest_framework.response import Response

import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend

from .models import MediaFile, Item
from .serializers import MediaFileSerializer, ItemSerializer

import mimetypes
from pathlib import Path

MEDIA_ROOT = "/app/media"

def index(request):
    return render(request, "mactaquac/home.html")

class MediaFileListView(generic.ListView):
    model = MediaFile
    context_object_name = "mediafiles"
    template_name = "mactaquac/filelist.html"


class MediaFileDetailView(generic.DetailView):
    model = MediaFile

class ItemListView(generic.ListView):
    model = Item

class ItemDetailView(generic.DetailView):
    model = Item

class MediaFileViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    queryset = MediaFile.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["filename", "item__identifier", "type"]

class ItemViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    lookup_field = "identifier" 

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["identifier", "collection", "updated"]

def download_media(request, filename):
    filepath = MediaFile.objects.get(filename=filename).filepath
    safe_path: Path = Path(MEDIA_ROOT) / filepath
    if not str(safe_path).startswith(MEDIA_ROOT):
        raise Http404("Invalid file path.")

    elif not safe_path.exists():
        raise Http404("File not found.")

    else:
        mime_type, _ = mimetypes.guess_type(safe_path)

        return FileResponse(
            open(safe_path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type=mime_type or "application/octet-stream",
        )
