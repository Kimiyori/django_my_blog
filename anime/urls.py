from django.urls import path
from anime.views import StudiosList,AnimeList,AnimeDetail

urlpatterns = [
    path('studios/', StudiosList.as_view(),name='studio_list'),
    path('<uuid:pk>',AnimeDetail.as_view(), name='anime_detail'), 
    path('', AnimeList.as_view(),name='anime_list'),
]