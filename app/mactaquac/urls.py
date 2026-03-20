from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "mactaquac"

router = routers.DefaultRouter()
router.register(r"mediafile", views.MediaFileViewSetSerialized)
router.register(r"item", views.ItemViewSetSerialized)

urlpatterns = [
    path("", views.index, name="index"),
    path("mediafiles/", views.MediaFileListView.as_view(), name="mediafiles"),
    path("mediafiles/<int:pk>/", views.MediaFileDetailView.as_view(), name="mediafile"),
    path("api/", include(router.urls), name="api"),
    path("download/<str:filename>/", views.download_media, name="download_media"),
    path("add_files/", views.add_new_files, name="add_files"),
    path("item_info/", views.new_item_info_view, name="item_info"),
    path("add_checksums/", views.add_checksums_view, name="add_checksums"),
    path("prune_deleted/", views.prune_deleted_view, name="prune_deleted"),
]
