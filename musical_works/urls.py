from .views import MusicWorkViewSet
from rest_framework import routers

app_name = 'works'

router = routers.SimpleRouter()
router.register(r'', MusicWorkViewSet, basename='music_work')

urlpatterns = []

urlpatterns += router.urls
