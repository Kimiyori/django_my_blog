from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import AnimeList, DemographicList, MagazineList, MangaList, PostList, GenreList, PublisherList, ThemeList
router = SimpleRouter()
router.register('anime', AnimeList, basename='anime')
router.register('manga', MangaList, basename='manga')
router.register('post', PostList, basename='post')
urlpatterns = [
    path('api-auth', include('rest_framework.urls'), name='rest_framework'),
    path('genres', GenreList.as_view(), name='api_genres'),
    path('publishers', PublisherList.as_view(), name='api_publishers'),
    path('demographics', DemographicList.as_view(), name='api_demographics'),
    path('themes', ThemeList.as_view(), name='api_themes'),
    path('magazines', MagazineList.as_view(), name='api_magazines'),

]

urlpatterns += router.urls
