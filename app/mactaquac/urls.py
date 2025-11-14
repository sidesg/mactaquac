from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "mactaquac"

router = routers.DefaultRouter()
router.register(r"mediafile", views.MediaFileViewSetSerialized)
router.register(r"item", views.ItemViewSetSerialized)

urlpatterns = [
    path("", views.index, name="index"),
    path("api/", include(router.urls), name="api")
]
