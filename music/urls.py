from rest_framework.routers import DefaultRouter

from music.views import AlbumViewSet, TrackViewSet

router = DefaultRouter()
router.register('album', viewset=AlbumViewSet)
router.register('track', viewset=TrackViewSet)

urlpatterns = router.get_urls()