from django.urls import path,include
from rest_framework.routers import SimpleRouter
from .views import AnimeList,MangaList, PostList
router = SimpleRouter()
router.register('anime', AnimeList, basename='anime')
router.register('manga', MangaList, basename='manga')
router.register('post', PostList, basename='post')
urlpatterns=[
    path('api-auth', include('rest_framework.urls'))
]

urlpatterns += router.urls