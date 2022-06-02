from api.permissions import IsAdminOrReadOnly
from post.models import Post
from rest_framework import status,viewsets, permissions
from titles.models import Anime,Manga,Genre
from .serializers import AnimeSerializer,MangaSerializer, PostSerializer
from .pagination import StandardResultsSetPagination
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status

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
    


class MangaList(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsAdminOrReadOnly,) 
    queryset = Manga.objects.select_related(
                            'demographic',
                            'authors__artist',
                            'authors__author',
                            'type',
                            'title',
                            'image').prefetch_related(
                                            'genre',
                                            'theme',
                                            'magazine',
                                            'publisher',)
    serializer_class = MangaSerializer



class PostList(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,) 
    queryset = Post.objects.select_related(
                                'author',
                                'related_to__manga__title',
                                'related_to__anime__title')
    serializer_class = PostSerializer

