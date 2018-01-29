from rest_framework import serializers

from music.mixins import WritableNestedModelSerializer
from music.models import Track, Album


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'order', 'title', 'duration', 'album')
        read_only_fields = ('album',)


class AlbumSerializer(WritableNestedModelSerializer):
    tracks = TrackSerializer(many=True)

    class Meta:
        model = Album
        fields = ('id', 'album_name', 'artist', 'tracks')
        writable_nested_fields = {'tracks': 'album'}