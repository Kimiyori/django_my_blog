
from api.permissions import IsAdminOrReadOnly
from post.models import Post
from rest_framework import status, viewsets, permissions
from titles.models import Anime, Demographic, Magazine, Manga, Genre, Publisher, Theme
from .serializers import AnimeSerializer, MangaSerializer, PostSerializer, GenreSerializer
from .pagination import StandardResultsSetPagination
from rest_framework.response import Response
from rest_framework import status

from rest_framework.response import Response

from django.core.cache import cache
from rest_framework import generics

CACHE_TIME = 60*5


class EnablePartialUpdateMixin:
    """Enable partial updates

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class AnimeList(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Anime.objects.select_related(
        'type',
        'title',
        'image',).prefetch_related(
        'genre',
        'theme',
        'studio',)
    serializer_class = AnimeSerializer


class MangaList(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, ]

    serializer_class = MangaSerializer

    def get_queryset(self,):
        query = Manga.objects.select_related('demographic', 'authors__artist', 'authors__author',
                                             'type', 'title', 'image').prefetch_related(
            'genre', 'theme', 'magazine',
            'publisher', 'related_post')
        return query

    def retrieve(self, request, pk=None):
        key = f'api:{pk}:manga'
        queryset = cache.get(key)

        if queryset is None:
            queryset = self.get_queryset().get(pk=pk)
            serializer_context = {
                'request': request,
            }
            queryset = MangaSerializer(
                queryset, context=serializer_context, partial=True).data
            cache.set(key, queryset, CACHE_TIME)

        return Response(queryset)


class GenreList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Genre.objects.all()

    def list(self, request):
        return Response(self.get_queryset().values_list("name", flat=True))


class ThemeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Theme.objects.all()

    def list(self, request):
        return Response(self.get_queryset().values_list("name", flat=True))


class PublisherList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Publisher.objects.all()

    def list(self, request):
        return Response(self.get_queryset().values_list("name", flat=True))


class DemographicList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Demographic.objects.all()

    def list(self, request):
        return Response(self.get_queryset().values_list("name", flat=True))


class MagazineList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Magazine.objects.all()

    def list(self, request):
        return Response(self.get_queryset().values_list("name", flat=True))


class PostList(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Post.objects.select_related(
        'author',
        'related_to__manga__title',
        'related_to__anime__title')
    serializer_class = PostSerializer
