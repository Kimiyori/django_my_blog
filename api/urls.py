from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import AnimeList,MangaList,GenreList
router = SimpleRouter()
router.register('anime', AnimeList, basename='anime')
router.register('manga', MangaList, basename='manga')
router.register('genre', GenreList, basename='genre')
urlpatterns = router.urls