from django.core.management.base import CommandError
from django.core.management import call_command
from django.test import TransactionTestCase
from unittest.mock import patch

from musical_works.models import Work, Contributor


class CommandsTestCase(TransactionTestCase):
    def test_reconcile_no_existing_file(self):
        """Test wrong file path passed"""
        args = ['wrong/path.csv']
        opts = {}
        with self.assertRaises(CommandError) as err:
            call_command('reconcile', *args, **opts)
        self.assertEqual(
            err.exception.args[0],
            f'The file specified {args[0]} was not found, please enter a valid file'
        )

    @patch('musical_works.management.commands.reconcile.process_work_with_iswc')
    @patch('musical_works.management.commands.reconcile.process_work_without_iswc')
    def test_reconcile_success(self, mock_no_iswc_work_function, mock_iswc_work_function):
        """
        Test Command called correctly and records processed as expected
        """
        args = ['musical_works/tests/mocks/valid_works_metadata.csv']
        opts = {}

        self.assertEqual(Work.objects.count(), 0)
        self.assertEqual(Contributor.objects.count(), 0)

        call_command('reconcile', *args, **opts)

        mock_iswc_work_function.assert_called()
        self.assertEqual(mock_iswc_work_function.call_count, 2)
        mock_no_iswc_work_function.assert_called_once()
