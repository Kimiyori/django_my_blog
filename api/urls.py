from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import permissions  # new
from drf_yasg.views import get_schema_view  # new
from drf_yasg import openapi  # new
from rest_framework.schemas import get_schema_view as shemas
from .views import AnimeList, DemographicList, MagazineList, MangaList, PostList, GenreList, PublisherList, ThemeList


schema_view = get_schema_view(  # new
    openapi.Info(
        title="Blog API",
        default_version="v1",
        description="A sample API for learning DRF",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="hello@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


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

    path('swagger/', schema_view.with_ui(  # new
        'swagger', cache_timeout=0), name='schema-swagger-ui'), 
    path('redoc/', schema_view.with_ui(  # new
        'redoc', cache_timeout=0), name='schema-redoc'),
    path('openapi', shemas(  # new
        title="Blog API",
        description="A sample API for learning DRF",
        version="1.0.0"
    ), name='openapi-schema'),


]

urlpatterns += router.urls
