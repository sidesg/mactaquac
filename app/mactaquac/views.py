from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from rest_framework import viewsets
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import MediaFile, Item
from .serializers import MediaFileSerializer, ItemSerializer
from .forms import MediaFileSearchForm

from pathlib import Path

MEDIA_ROOT = "/home/app/web/media"

def index(request):
    return render(request, "mactaquac/home.html")

class MediaFileListView(generic.FormView):
    template_name = "mactaquac/filelist.html"
    
    def get(self, request, *args, **kwargs):
        form = MediaFileSearchForm(self.request.GET or None)

        if form.is_valid():
            query_set = MediaFile.objects.all()
            item_identifier = request.GET.get("item_identifier")
            collection = request.GET.get("collection")
            title = request.GET.get("title")
            filename = request.GET.get("filename")

            if item_identifier:
                query_set = query_set.filter(item__identifier=item_identifier.strip().upper())
            if collection:
                query_set = query_set.filter(item__collection=collection.strip().upper())
            if title:
                query_set = query_set.filter(item__title__contains=title.strip())
            if filename:
                query_set = query_set.filter(filename__contains=filename)
        else:
            # query_set = None
            query_set = MediaFile.objects.all()

        paginator = Paginator(query_set, 25)
        page = self.request.GET.get('page')
        try:
            query_set = paginator.page(page)
        except PageNotAnInteger:
            query_set = paginator.page(1)
        except EmptyPage:
            query_set = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(form=form, mediafiles=query_set)) 

class MediaFileDetailView(generic.DetailView):
    model = MediaFile
    template_name = "mactaquac/mediafile.html"
    
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
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # This tells Nginx to serve the file
        response['X-Accel-Redirect'] = f"/media/{filepath}"

        return response
    