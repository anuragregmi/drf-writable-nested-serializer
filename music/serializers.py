from rest_framework import serializers

from music.models import Track, Album


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'order', 'title', 'duration', 'album')
        read_only_fields = ('album',)


class AlbumSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)

    class Meta:
        model = Album
        fields = ('id', 'album_name', 'artist', 'tracks')

    def create(self, validated_data):
        tracks_data = validated_data.pop('tracks')
        album = Album.objects.create(**validated_data)
        for track_data in tracks_data:
            Track.objects.create(album=album, **track_data)
        return album

    def update(self, instance, validated_data):
        validated_data.pop('tracks')
        tracks_data = self.initial_data.get('tracks')
        if tracks_data:
            for track_data in tracks_data:
                tr_id = track_data.get('id')
                if tr_id:
                    try:
                        track = Track.objects.get(id=tr_id)
                        track_sr = TrackSerializer(instance=track, data=track_data, partial=self.partial)
                        if track_sr.is_valid():
                            track_sr.save()
                        else:
                            raise serializers.ValidationError(track_sr.data)
                    except Track.DoesNotExist:
                        raise serializers.ValidationError('No object found to update for id={}'.format(tr_id))
                    except serializers.ValidationError as e:
                        raise e
                else:
                    Track.objects.create(album=instance, **track_data)

        instance = super().update(instance, validated_data)

        return instance
