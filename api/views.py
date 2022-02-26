from rest_framework import status,viewsets, permissions
from anime.models import Anime
from manga.models import Manga,Genre
from .serializers import AnimeSerializer,MangaSerializer,GenreSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class AnimeList(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,) 
    queryset = Anime.objects.all()
    serializer_class = AnimeSerializer
    


class MangaList(viewsets.ModelViewSet):
    
    queryset = Manga.objects.all()
    serializer_class = MangaSerializer


class GenreList(viewsets.ModelViewSet):
    
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer