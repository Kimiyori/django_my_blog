from django.urls import path
from .views import PostList, ContentCreateUpdateView, PostDetail, PostDetailChange, PostUpdate, ContentDeleteView,ContentOrderView
urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<uuid:pk>', PostDetail.as_view(), name='post_detail'),
    path('<uuid:pk>/v1/', PostUpdate.as_view(), name='post_detail_change1'),
    path('<uuid:pk>/change/', PostDetailChange.as_view(),
         name='post_detail_change'),
    path('<uuid:post_id>/content/create/<model_name>',
         ContentCreateUpdateView.as_view(),
         name='module_content_create'),
    path('<uuid:post_id>/content/create/<model_name>/<order>',
         ContentCreateUpdateView.as_view(),
         name='module_content_create'),

    path('<uuid:post_id>/content/<model_name>/<id>/',
         ContentCreateUpdateView.as_view(),
         name='module_content_update'),

    path('content/<uuid:post_id>/<int:id>/delete/',
         ContentDeleteView.as_view(),
         name='content_delete'),
     path('content/order/',
          ContentOrderView.as_view(),
          name='content_order'),
]
