from django.urls import path
from .views import TitleList,TitleDetail
urlpatterns = [path('manga/', TitleList.as_view(),name='manga_list'),
                path('anime/', TitleList.as_view(),name='anime_list'),
              path('<uuid:pk>',TitleDetail.as_view(), name='title_detail'),]