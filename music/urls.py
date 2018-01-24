from rest_framework.routers import DefaultRouter

from music.views import AlbumViewSet, TrackViewSet

router = DefaultRouter()
router.register('album', viewset=AlbumViewSet, base_name='album')
router.register('track', viewset=TrackViewSet, base_name='track')

urlpatterns = router.get_urls()