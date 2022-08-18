
import uuid
from api.permissions import IsAdminOrReadOnly
from post.models import Content, Post
from rest_framework import  viewsets, permissions
from titles.models import Anime, Demographic, Magazine, Manga, Genre, Publisher, Theme
from .serializers import AnimeSerializer, DemographicSerializer, MagazineSerializer, MangaSerializer, PostSerializer, GenreSerializer, PublisherSerializer, ThemeSerializer
from .pagination import StandardResultsSetPagination
from rest_framework.response import Response

from django.db.models import Prefetch
from rest_framework.response import Response

from rest_framework import generics
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging
from django.db.models import QuerySet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
  
CACHE_TIME = 60*5

file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')


class EnablePartialUpdateMixin:
    """Enable partial updates

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class AnimeList(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, ]
    serializer_class = AnimeSerializer

    def get_queryset(self) -> QuerySet:
        query = Anime.objects.select_related('type', 'title', 'image').prefetch_related(
            'genre', 'theme', 'studio', 'related_post')
        return query

    def list(self, request):
        console_logger.info('Get list of anime titles with api')
        return super().list(request)

    @method_decorator(cache_page(CACHE_TIME))
    def retrieve(self, request, pk: uuid.UUID = None) -> Response:
        console_logger.info(f'Get anime title with following {pk} with api')
        queryset = self.get_queryset().get(pk=pk)
        serializer_context = {
            'request': request,
        }
        arguments = {'instance': queryset,
                     'context': serializer_context,
                     'partial': True}
        fields = request.query_params.get('fields')
        if fields:
            arguments['fields'] = fields.split(',')

        queryset = AnimeSerializer(**arguments).data
        console_logger.info(f'Successful get api anime title with following id {pk} with api', extra={
            'fields': fields})
        return Response(queryset)


class MangaList(EnablePartialUpdateMixin, viewsets.ModelViewSet):

    pagination_class = StandardResultsSetPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, ]

    serializer_class = MangaSerializer

    def get_queryset(self) -> QuerySet:
        query = Manga.objects.select_related('demographic', 'authors__artist', 'authors__author',
                                             'type', 'title', 'image').prefetch_related(
            'genre', 'theme', 'magazine',
            'publisher', 'related_post')
        return query

    def list(self, request):
        console_logger.info('Get list of manga titles with api')
        return super().list(request)

    @method_decorator(cache_page(CACHE_TIME))
    def retrieve(self, request, pk=None):
        console_logger.info(f'Get manga title with following {id}')
        queryset = self.get_queryset().get(pk=pk)
        serializer_context = {
            'request': request,
        }
        arguments = {'instance': queryset,
                     'context': serializer_context, 'partial': True}
        fields = request.query_params.get('fields')
        if fields:
            arguments['fields'] = fields.split(',')

        queryset = MangaSerializer(**arguments).data
        console_logger.info(f'Successful get api manga title with following id {id}', extra={
            'fields': fields})
        return Response(queryset)


class GenreList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def list(self, request):
        console_logger.info('Get list of genres with api')
        return Response(self.get_queryset().values_list("name", flat=True))


class ThemeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

    def list(self, request):
        console_logger.info('Get list of themes  with api')
        return Response(self.get_queryset().values_list("name", flat=True))


class PublisherList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializerserializer_class = PublisherSerializer

    def list(self, request):
        console_logger.info('Get list of publishers with api')
        return Response(self.get_queryset().values_list("name", flat=True))


class DemographicList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Demographic.objects.all()
    serializer_class = DemographicSerializer

    def list(self, request):
        console_logger.info('Get list of demographic with api')
        return Response(self.get_queryset().values_list("name", flat=True))


class MagazineList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Magazine.objects.all()
    serializer_class = MagazineSerializer

    def list(self, request):
        console_logger.info('Get list of magazines with api')
        return Response(self.get_queryset().values_list("name", flat=True))


class PostList(viewsets.ReadOnlyModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, ]

    serializer_class = PostSerializer

    def list(self, request):
        console_logger.info('Get list of posts with api')
        return super().list(request)

    def get_queryset(self,):
        query = Post.objects.select_related(
            'author',
        ).prefetch_related(
            Prefetch('contents', queryset=Content.objects.all(
            ).prefetch_related('item', 'content_type'))
        )
        return query

    @method_decorator(cache_page(CACHE_TIME))
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset().get(pk=pk)
        serializer_context = {
            'request': request,
        }
        arguments = {'instance': queryset,
                     'context': serializer_context, 'partial': True}
        fields = request.query_params.get('fields')
        if fields:
            arguments['fields'] = fields.split(',')
        queryset = PostSerializer(**arguments).data

        return Response(queryset)



class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
