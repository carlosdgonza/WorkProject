from django.test import TestCase
from unittest.mock import patch

from musical_works.models import Work, Contributor
from musical_works.utils import process_work_with_iswc, process_work_without_iswc


class WorkProcessingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.existing_work = Work.objects.create(iswc='1', title='Title 1')
        cls.first_existing_contributor = Contributor.objects.create(full_name='First Contributor')
        cls.second_existing_contributor = Contributor.objects.create(full_name='Second Contributor')

        cls.first_existing_contributor.works.add(cls.existing_work)
        cls.second_existing_contributor.works.add(cls.existing_work)

    def test_process_work_with_iswc_and_new_contributor(self):
        """Test existing work updates its contributors by adding the new one"""
        work_dict = {'iswc': '1', 'title': 'Title 1', 'contributors': ['Third Contributor']}

        self.assertEqual(self.existing_work.contributors.count(), 2)
        process_work_with_iswc(work_dict)
        self.assertEqual(self.existing_work.contributors.count(), 3)
        new_contributor = Contributor.objects.get(full_name='Third Contributor')
        self.assertEqual(new_contributor.works.first(), self.existing_work)

    def test_process_work_with_new_iswc_but_same_title_and_or_contributors(self):
        """Test new work is added although has the same title and contributors (It is a new iswc)"""
        works_dict = [
            {'iswc': '2', 'title': 'Title 1', 'contributors': ['First Contributor', 'Second Contributor']},
            {'iswc': '3', 'title': 'Title 1', 'contributors': ['Third Contributor']}
        ]

        with self.subTest('Same title and same contributors. New work created. No new contributors created'):
            self.assertEqual(Work.objects.count(), 1)
            self.assertEqual(Contributor.objects.count(), 2)
            process_work_with_iswc(works_dict[0])
            self.assertEqual(Work.objects.count(), 2)
            self.assertEqual(Contributor.objects.count(), 2)

        with self.subTest('Same title and different contributors. New work created. New contributor created'):
            self.assertEqual(Work.objects.count(), 2)
            self.assertEqual(Contributor.objects.count(), 2)
            process_work_with_iswc(works_dict[1])
            self.assertEqual(Work.objects.count(), 3)
            self.assertEqual(Contributor.objects.count(), 3)

    def test_process_work_with_new_iswc_but_no_title(self):
        """Test new work is no created because no title associated"""
        work_dict = {'iswc': '2', 'title': '', 'contributors': ['First Contributor', 'Third Contributor']}

        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        process_work_with_iswc(work_dict)
        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)

    def test_process_work_without_iswc_but_matching_title_and_one_contributor(self):
        """Test no iswc passed, but title and contributor match. Work's contributors are updated"""
        work_dict = {'iswc': '', 'title': 'Title 1', 'contributors': ['First Contributor', 'Third Contributor']}

        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        self.assertEqual(self.existing_work.contributors.count(), 2)
        process_work_without_iswc(work_dict)
        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 3)
        self.assertEqual(self.existing_work.contributors.count(), 3)

    def test_process_work_without_iswc_matching_title_but_not_matching_contributor(self):
        """Test no iswc passed, title matches, but contributor doesn't. No work or contributor is added"""
        work_dict = {'iswc': '', 'title': 'Title 1', 'contributors': ['Third Contributor']}

        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        self.assertEqual(self.existing_work.contributors.count(), 2)
        process_work_without_iswc(work_dict)
        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        self.assertEqual(self.existing_work.contributors.count(), 2)

    def test_process_work_without_iswc_no_matching_title(self):
        """Test no iswc passed, title doesn't match. No work or contributor is added"""
        work_dict = {'iswc': '', 'title': 'Title 2', 'contributors': ['First Contributor']}

        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        self.assertEqual(self.existing_work.contributors.count(), 2)
        process_work_without_iswc(work_dict)
        self.assertEqual(Work.objects.count(), 1)
        self.assertEqual(Contributor.objects.count(), 2)
        self.assertEqual(self.existing_work.contributors.count(), 2)

    @patch('musical_works.utils.logger')
    def test_process_work_with_iswc_but_no_title(self, logger_mock):
        """Test iswc passed, but no title passed for new record won't be added"""
        work_dict = {'iswc': '2', 'title': '', 'contributors': ['First Contributor']}
        contributors = work_dict.get('contributors', [])

        process_work_with_iswc(work_dict)
        logger_mock.info.assert_called_with(
            f'Work not added for missing title.'
            f'ISWC: {work_dict.get("iswc", "")} - Contributors: {",".join(contributors)}'
        )

    @patch('musical_works.utils.logger')
    def test_process_work_without_iswc_and_multiple_matching_records(self, logger_mock):
        """Test iswc passed, but no title passed for new record won't be added"""
        new_existing_work = Work.objects.create(iswc='2', title='Title 1')
        new_existing_contributor = Contributor.objects.create(full_name='Third Contributor')
        new_existing_contributor.works.add(new_existing_work)
        self.first_existing_contributor.works.add(new_existing_work)
        work_dict = {'iswc': '', 'title': 'Title 1', 'contributors': ['First Contributor']}
        contributors = work_dict.get('contributors', [])

        process_work_without_iswc(work_dict)
        logger_mock.info.assert_called_with(
            f'Multiple works match for title {work_dict.get("title", "")} and contributors'
            f' {",".join(contributors)}'
        )
