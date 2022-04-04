from django.urls import path
from anime.views import AnimeList,AnimeDetail,SearchResultsList
urlpatterns = [
    path('', AnimeList.as_view(),name='anime_list'),
    path('<uuid:pk>',AnimeDetail.as_view(), name='anime_detail'),
    path('search/', SearchResultsList.as_view(), name='anime_search'),
    ]