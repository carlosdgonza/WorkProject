import numpy as np
import dask.dataframe as dd
from django.core.exceptions import ValidationError
from concurrent.futures import ThreadPoolExecutor


from django.core.management.base import BaseCommand, CommandError
from musical_works.utils import process_work_with_iswc, process_work_without_iswc


class Command(BaseCommand):
    help = 'Store reconciled works'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        # Load csv file into a Dask Dataframe
        try:
            df = dd.read_csv(options['file'])
        except FileNotFoundError:
            raise CommandError(f'The file specified {options["file"]} was not found, please enter a valid file')

        # Separate contributors by '|' into list
        df['contributors'] = df.contributors.str.split('|')

        # Separate records with ISWC code and without it
        works_df_nan_iswc = df[df['iswc'].isna()].replace(np.nan, '')
        works_df_with_iswc = df[df['iswc'].isna() == False].replace(np.nan, '')
        # import pdb;pdb.set_trace()

        # Define Custom aggregation method over Dataframe to join contributors for same ISWC
        str_join = dd.Aggregation(
            'str_join',
            lambda x: x.apply(lambda y: list({elem for l in y for elem in l if elem})),
            lambda contributors_join: contributors_join.apply(lambda y: list({elem for l in y for elem in l if elem})),
        )

        # Union of same ISWC contributors
        works_df_by_iswc = works_df_with_iswc.groupby('iswc').agg(
            {'title': 'first', 'contributors': str_join}).reset_index()

        # import pdb;pdb.set_trace()
        # New Dask Dataframe to be processed without ISWC duplicates
        # new_works_df = dd.concat([works_df_by_iswc, works_df_nan_iswc], sort=False, ignore_index=True)

        # Process Work Music concurrently
        # with ThreadPoolExecutor() as executor:
        #     executor.map(process_work, new_works_df.iterrows(), timeout=30)

        for row in works_df_by_iswc.iterrows():
            process_work_with_iswc(row)

        for row in works_df_nan_iswc.iterrows():
            process_work_without_iswc(row)
