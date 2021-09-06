import numpy as np
import dask.dataframe as dd
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
        works_df_nan_iswc = df[df['iswc'].isna()][df.title.notnull()].replace(np.nan, '')
        works_df_with_iswc = df[df['iswc'].isna() == False].replace(np.nan, '')
        # import pdb;pdb.set_trace()

        # Define Custom aggregation method over Dataframe to join contributors for same ISWC
        str_join = dd.Aggregation(
            'str_join',
            lambda x: x.apply(lambda y: list({elem for cont_list in y for elem in cont_list if elem})),
            lambda contributors_join: contributors_join.apply(lambda y: list({elem for cont_list in y for elem in cont_list if elem})),
        )

        # Union of same ISWC contributors
        works_df_by_iswc = works_df_with_iswc.groupby('iswc').agg(
            {'title': 'first', 'contributors': str_join}).reset_index()

        # Process Work Music concurrently
        # import pdb;pdb.set_trace()
        with ThreadPoolExecutor() as executor:
            # for row in works_df_by_iswc.iterrows():
            #     executor.submit(process_work_with_iswc, row[1].to_dict())
            # for row in works_df_nan_iswc.iterrows():
            #     executor.submit(process_work_without_iswc, row[1].to_dict())
            # import pdb;pdb.set_trace()
            executor.map(process_work_with_iswc, works_df_by_iswc.iterrows(), timeout=30)
            executor.map(process_work_without_iswc, works_df_nan_iswc.iterrows(), timeout=30)
