from django.urls import path
from .views import ProfileDetail

urlpatterns = [
    path("profile/<int:pk>/", ProfileDetail.as_view(), name="profile_detail"),
]
