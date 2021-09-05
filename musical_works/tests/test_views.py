from django.shortcuts import reverse
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status

from musical_works.models import Work, Contributor


class WorkViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.work = Work.objects.create(
            title='Song Title',
            iswc='T0000000000'
        )
        cls.contributor = Contributor.objects.create(full_name='Contributor First Last Name')
        cls.contributor.work.add(cls.work)

    def test_get_success(self):
        """Call to endpoint must succeed when is passed a valid ISWC code."""
        endpoint = reverse('works:music_work-detail', kwargs={'iswc': self.work.iswc})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.work.title)
        self.assertEqual(response.data['iswc'], self.work.iswc)
        self.assertEqual(response.data['contributors'][0]['full_name'], self.contributor.full_name)
        self.assertEqual(len(response.data['contributors']), 1)

    def test_get_failed_unknown_iswc(self):
        """Call to endpoint must fail when is passed a wrong ISWC code."""
        endpoint = reverse('works:music_work-detail', kwargs={'iswc': 'wrong'})

        response = self.client.get(endpoint)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
