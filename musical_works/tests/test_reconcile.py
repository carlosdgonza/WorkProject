from django.shortcuts import reverse
from django.core.management.base import CommandError
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from rest_framework import status
from asgiref.sync import async_to_sync
from musical_works.models import Work, Contributor

from django.core.management import call_command
from django.test import TestCase, TransactionTestCase
import pytest


class CommandsTestCase(TransactionTestCase):
    def test_reconcile_no_existing_file(self):
        " Test my custom command."
        args = ['wrong/path.csv']
        opts = {}
        with self.assertRaises(CommandError) as err:
            call_command('reconcile', *args, **opts)
        self.assertEqual(
            err.exception.args[0],
            f'The file specified {args[0]} was not found, please enter a valid file'
        )

    # @pytest.mark.django_db(transaction=True)
    def test_reconcile_success(self):
        " Test my custom command."
        args = ['musical_works/tests/mocks/valid_works_metadata.csv']
        opts = {}

        self.assertEqual(Work.objects.count(), 0)
        self.assertEqual(Contributor.objects.count(), 0)

        call_command('reconcile', *args, **opts)

        self.assertEqual(Work.objects.count(), 2)
        self.assertEqual(Contributor.objects.count(), 2)

    def test_reconcile_wrong_record(self):
        " Test my custom command."
        args = ['musical_works/tests/mocks/invalid_works_metadata.csv']
        opts = {}

        self.assertEqual(Work.objects.count(), 0)
        self.assertEqual(Contributor.objects.count(), 0)

        call_command('reconcile', *args, **opts)

        self.assertEqual(Work.objects.count(), 0)
        self.assertEqual(Contributor.objects.count(), 0)




# class WorkViewSetTestCase(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         # cls.work = Work.objects.create(
#         #     title='Song Title',
#         #     iswc='T0000000000'
#         # )
#         # cls.contributor = Contributor.objects.create(full_name='Contributor First Last Name')
#         # cls.contributor.work.add(cls.work)
#
#     def test_get_success(self):
#         """Call to endpoint must succeed when is passed a valid ISWC code."""
#         endpoint = reverse('works:music_work-detail', kwargs={'iswc': self.work.iswc})
#
#         response = self.client.get(endpoint)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['title'], self.work.title)
#         self.assertEqual(response.data['iswc'], self.work.iswc)
#         self.assertEqual(response.data['contributors'][0]['full_name'], self.contributor.full_name)
#         self.assertEqual(len(response.data['contributors']), 1)
#
#     def test_get_failed_unknown_iswc(self):
#         """Call to endpoint must fail when is passed a wrong ISWC code."""
#         endpoint = reverse('works:music_work-detail', kwargs={'iswc': 'wrong'})
#
#         response = self.client.get(endpoint)
#
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)