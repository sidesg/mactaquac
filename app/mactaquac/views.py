from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.views import generic
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from rest_framework import viewsets

from django_filters.rest_framework import DjangoFilterBackend

from .models import MediaFile, Item, Wrapper, VideoCodec, AudioCodec
from .serializers import MediaFileSerializer, ItemSerializer
from .forms import MediaFileSearchForm, MediaFileFilterForm

from pathlib import Path

MEDIA_ROOT = "/home/app/web/media"

def index(request):
    return render(request, "mactaquac/home.html")
  
class MediaFileListView(generic.FormView):
    template_name = "mactaquac/filelist.html"
    
    def get(self, request, *args, **kwargs):
        form = MediaFileSearchForm(self.request.GET or None)

        #declare variables for initial landing on list page
        query_set = MediaFile.objects.all().order_by("item__identifier", "filename")
        item_identifier = str()
        collection = str()
        title = str()
        filename = str()
        media_wrapper = None
        dimensions_width = None
        video_codec = None
        audio_codec = None

        #Change possible values of filter categories based on query set unique values
        wrapper_list = Wrapper.objects.all()
        vcodec_list = VideoCodec.objects.all()
        acodec_list = AudioCodec.objects.all()

        if form.is_valid():
            #Get data from request
            item_identifier = request.GET.get("item_identifier")
            collection = request.GET.get("collection")
            title = request.GET.get("title")
            filename = request.GET.get("filename")
            media_wrapper = request.GET.getlist("media_wrapper", None)
            video_codec = request.GET.getlist("video_codec", None)
            audio_codec = request.GET.getlist("audio_codec", None)
            dimensions_width = request.GET.get("dimensions_width", None)

            #Filter query set with search
            if item_identifier:
                query_set = query_set.filter(item__identifier=item_identifier.strip().upper())
            if collection:
                query_set = query_set.filter(item__collection=collection.strip().upper())
            if title:
                query_set = query_set.filter(item__title__contains=title.strip())
            if filename:
                query_set = query_set.filter(filename__contains=filename)

            #Make list of filter values before applying the filters
            wrapper_list = Wrapper.objects.filter(id__in=query_set.values("wrapper"))
            vcodec_list = VideoCodec.objects.filter(id__in=query_set.values("videocodec"))
            acodec_list = AudioCodec.objects.filter(id__in=query_set.values("audiocodec"))

            if media_wrapper:
                query_set = query_set.filter(wrapper__name__in=media_wrapper)
            if video_codec:
                query_set = query_set.filter(videocodec__name__in=video_codec)
            if audio_codec:
                query_set = query_set.filter(audiocodec__name__in=audio_codec)
            if dimensions_width:
                query_set = query_set.filter(width__gt=dimensions_width)

        #Set up pagination of query set
        paginator = Paginator(query_set, 25)
        page = request.GET.get('page')
        try:
            query_set = paginator.page(page)
        except PageNotAnInteger:
            query_set = paginator.page(1)
        except EmptyPage:
            query_set = paginator.page(paginator.num_pages)

        #add filter form with inherited intial values
        filter_form = MediaFileFilterForm(
            initial={
                "media_wrapper": media_wrapper if media_wrapper else None,
                "video_codec": video_codec if video_codec else None,
                "audio_codec": audio_codec if audio_codec else None,
                "dimensions_width": dimensions_width if dimensions_width else None,
                "item_identifier": item_identifier if item_identifier else None,
                "collection": collection if collection else None,
                "title": title if title else None,
                "filename": filename if filename else None
            },
            wrapper_list=wrapper_list,
            vcodec_list=vcodec_list,
            acodec_list=acodec_list
        )

        return self.render_to_response(self.get_context_data(form=form, mediafiles=query_set, filter_form=filter_form)) 

class MediaFileDetailView(generic.DetailView):
    model = MediaFile
    template_name = "mactaquac/mediafile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["duplicates"] = MediaFile.find_duplicates()
        return context
    
class MediaFileViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = MediaFileSerializer
    queryset = MediaFile.objects.all().order_by("id")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["filename", "item__identifier", "type", "checksum"]

class ItemViewSetSerialized(viewsets.ModelViewSet):
    serializer_class = ItemSerializer
    queryset = Item.objects.all().order_by("identifier")
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
    