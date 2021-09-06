from django.core.exceptions import ValidationError
from django.db import transaction
import logging
from musical_works.models import Work, Contributor

logger = logging.getLogger(__name__)


def process_work_without_iswc(row):
    musical_work=row[1].to_dict()
    contributors = musical_work.pop('contributors', [])
    with transaction.atomic():
        works_queryset = Work.objects.filter(
            title=musical_work.get('title', ''),
            contributors__full_name__in=contributors,
        ).distinct()

        if works_queryset.count() > 1:
            logger.info(
                f'Multiple works match for title {musical_work.get("title", "")} and contributors'
                f' {",".join(contributors)}'
            )

        work = works_queryset.first()
        if work:
            create_contributors(set(contributors), work)


def process_work_with_iswc(row):
    musical_work = row[1].to_dict()
    import pdb;pdb.set_trace()
    iswc = musical_work.get('iswc', '')
    contributors = musical_work.pop('contributors', [])
    work = None
    with transaction.atomic():
        try:
            work = Work.objects.get(iswc=iswc)
        except Work.DoesNotExist:
            try:
                work = Work.objects.create(**musical_work)
            except ValidationError:
                pass

        if work:
            create_contributors(set(contributors), work)


def create_contributors(contributors, work):
    for contributor in set(contributors):
        try:
            contributor_instance = Contributor.objects.get(full_name=contributor)
        except Contributor.DoesNotExist:
            contributor_instance = Contributor.objects.create(full_name=contributor)
        contributor_instance.work.add(work)
