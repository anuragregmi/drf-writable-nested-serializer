from rest_framework.viewsets import ModelViewSet

from music.models import Track, Album
from music.serializers import TrackSerializer, AlbumSerializer


class TrackViewSet(ModelViewSet):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()


class AlbumViewSet(ModelViewSet):
    serializer_class = AlbumSerializer
    queryset = Album.objects.all()
