from django.urls import path
from .views import PostList , ContentCreateUpdateView,PostDetail,PostDetailChange,PostUpdate
urlpatterns = [
    path('', PostList.as_view(),name='post_list'),
 path('<uuid:pk>',PostDetail.as_view(), name='post_detail'),
     path('<uuid:pk>/v1/',PostUpdate.as_view(), name='post_detail_change1'),
  path('<uuid:pk>/change/',PostDetailChange.as_view(), name='post_detail_change'),

    path('<uuid:post_id>/content/<model_name>/create/',
         ContentCreateUpdateView.as_view(),
         name='module_content_create'),

    path('<uuid:post_id>/content/<model_name>/<id>/',
         ContentCreateUpdateView.as_view(),
         name='module_content_update'),
 ]