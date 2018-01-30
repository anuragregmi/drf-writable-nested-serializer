from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from music.models import Album, Track


class TestAlbum(APITestCase):
    """
    Test nested serializer
    """

    def setUp(self):
        album = Album(album_name='Anti', artist='Rihanna')
        album.save()

        self.album_id = album.id

        track1 = Track(title='Desperado', order=1, album=album, duration=4)
        track1.save()

        self.track1_id = track1.id

        track2 = Track(title='Love on the brain', order=2, album=album, duration=3)
        track2.save()

        self.track2_id = track2.id

    def test_push(self):
        url = reverse('album-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.__len__(), 1)
        self.assertEqual(response.data[0].get('tracks').__len__(), 2)

        right_data = {
            "album_name": "ad",
            "artist": "asded",
            "tracks": [
                {
                    "title": "Despo", "order": 1, "duration": 4
                },
                {
                    "title": "Deo1", "order": 3, "duration": 4
                }
            ]
        }

        response = self.client.post(url, data=json.dumps(right_data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(url)
        self.assertEqual(response.data.__len__(), 2)
        self.assertEqual(response.data[0].get('tracks').__len__(), 2)
        self.assertEqual(response.data[1].get('tracks').__len__(), 2)

        wrong_data = {
            "album_name": "What's Going On",
            "artist": "Marvin Gaye One",
            "tracks": [
                {
                    "order": 1,
                    "album": 2
                },
                {
                    "order": 2,
                    "title": "What's happening brother",
                    "duration": 7,
                }
            ]
        }

        response = self.client.post(url, data=json.dumps(wrong_data), content_type='application/json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        url = reverse('album-detail', kwargs={'pk': self.album_id})

        data = {
            "album_name": "Updated Name",
            "tracks": [
                {
                    "id": self.track1_id,
                    "duration": 12
                }
            ]
        }

        response = self.client.patch(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Track.objects.get(id=self.track1_id).duration, 12)

    def test_put(self):
        url = reverse('album-detail', kwargs={'pk': self.album_id})

        data = {
            "album_name": "Anti",
            "artist": "Rihanna",
            "tracks": [
                {
                    "id": self.track1_id,
                    "title": "Despo",
                    "order": 1,
                    "duration": 4
                },
                {
                    "id": self.track2_id,
                    "title": "Love on the brain",
                    "order": 2,
                    "duration": 10
                },
            ]
        }

        response = self.client.patch(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(Track.objects.get(id=self.track1_id).title, "Despo")
        self.assertEqual(Track.objects.get(id=self.track2_id).duration, 10)
