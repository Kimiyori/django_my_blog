from django.urls import path
from .views import MangaList,GenreList,MangaDetail
urlpatterns = [path('', MangaList.as_view(),name='manga_list'),
              path('<uuid:pk>',MangaDetail.as_view(), name='manga_detail'),
              path('genre/<slug:slug>', GenreList.as_view(),name='genre_list')
]
"""urlpatterns = [
  
    path('studios/', StudiosList.as_view(),name='studio_list'),
      path('studios/<slug:slug>', StudiosDetailList.as_view(),name='studio_detail_list'),
    path('<uuid:pk>',AnimeDetail.as_view(), name='anime_detail'), 
    path('genres/<slug:slug>',GenreAnimeList.as_view(),name='anime_list_genre'),
    path('demographic/<slug:slug>',DemoAnimeList.as_view(),name='demo_list_genre'),
    path('', AnimeList.as_view(),name='anime_list'),
    ]"""