from rest_framework import mixins, viewsets

from musical_works.models import Work
from musical_works.serializers import WorkSerializer


# Create your views here.
class MusicWorkViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    View that shows the information related to specific ISWC code
    """
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    lookup_field = 'iswc'
