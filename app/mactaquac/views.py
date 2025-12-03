from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from rest_framework import viewsets
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import MediaFile, Item, Wrapper
from .serializers import MediaFileSerializer, ItemSerializer
from .forms import MediaFileSearchForm, MediaFileFilterForm

from pathlib import Path

MEDIA_ROOT = "/home/app/web/media"

def index(request):
    return render(request, "mactaquac/home.html")

class MediaFileListView(generic.View):
    template_name = "mactaquac/filelist.html"
    
class MediaFileListView(generic.FormView):
    template_name = "mactaquac/filelist.html"
    
    def get(self, request, *args, **kwargs):
        form = MediaFileSearchForm(self.request.GET or None)
        self.query_set = MediaFile.objects.all()
        self.item_identifier = str()
        self.collection = str()
        self.title = str()
        self.filename = str()

        if form.is_valid():
            self.query_set = MediaFile.objects.all()
            self.item_identifier = request.GET.get("item_identifier")
            self.collection = request.GET.get("collection")
            self.title = request.GET.get("title")
            self.filename = request.GET.get("filename")
            media_wrapper = request.GET.getlist("media_wrapper")
            dimensions_width = request.GET.get("dimensions_width")

            if self.item_identifier:
                self.query_set = self.query_set.filter(item__identifier=self.item_identifier.strip().upper())
            if self.collection:
                self.query_set = self.query_set.filter(item__collection=self.collection.strip().upper())
            if self.title:
                self.query_set = self.query_set.filter(item__title__contains=self.title.strip())
            if self.filename:
                self.query_set = self.query_set.filter(filename__contains=self.filename)
            if media_wrapper:
                self.query_set = self.query_set.filter(wrapper__name__in=media_wrapper)
            if dimensions_width:
                self.query_set = self.query_set.filter(width__gt=dimensions_width)

        paginator = Paginator(self.query_set, 25)
        page = self.request.GET.get('page')
        try:
            self.query_set = paginator.page(page)
        except PageNotAnInteger:
            self.query_set = paginator.page(1)
        except EmptyPage:
            self.query_set = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(form=form, mediafiles=self.query_set)) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = MediaFileFilterForm(
            Wrapper.objects.all(),
            data={
                "item_identifier": self.item_identifier if self.item_identifier else None,
                "collection": self.collection if self.collection else None,
                "title": self.title if self.title else None,
                "filename": self.filename if self.filename else None
            }
        )

        return context

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
    