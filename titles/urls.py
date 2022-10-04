from django.urls import path, re_path
from .views import TitleList, TitleDetail

urlpatterns = [
    path("manga/", TitleList.as_view(), name="manga_list"),
    path("anime/", TitleList.as_view(), name="anime_list"),
    path("manga/<uuid:pk>/", TitleDetail.as_view(), name="manga_detail"),
    path("anime/<uuid:pk>/", TitleDetail.as_view(), name="anime_detail"),
]
