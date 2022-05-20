# posts/serializers.py
from requests import post
from post.models import Post, Related
from rest_framework import serializers
from titles.models import Anime,Title,Manga,AuthorTable,Publisher,Demographic,MangaType,Genre,Authors,AuthorTable,Image


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['original_name', 'english_name', 'russian_name']

class AuthorTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorTable
        fields = ['name','photo']

class AuthorsSerializer(serializers.ModelSerializer):
    author=AuthorTableSerializer()

    artist= AuthorTableSerializer()

    class Meta:
        model = Authors 
        fields = ['author','artist']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image','thumbnail']
class MangaSerializer(serializers.ModelSerializer):
    authors=AuthorsSerializer()
    publisher=serializers.StringRelatedField(many=True)
    genre=serializers.StringRelatedField(many=True)
    theme=serializers.StringRelatedField(many=True)
    magazine=serializers.StringRelatedField(many=True)
    demographic=serializers.StringRelatedField()
    type=serializers.StringRelatedField()
    title  = TitleSerializer()
    image=ImageSerializer()
    class Meta:
        model = Manga
        fields = ['id','title','type','authors','publisher','premiere',
                    'volumes','chapters','genre','demographic','theme',
                                    'image','magazine','description']


 


class AnimeSerializer(serializers.ModelSerializer):
    title  = TitleSerializer()
    genre=serializers.StringRelatedField(many=True)
    theme=serializers.StringRelatedField(many=True)
    type=serializers.StringRelatedField()
    studio=serializers.StringRelatedField(many=True)
    image=ImageSerializer()
    class Meta:
        model = Anime
        fields = ('id','title','type', 'studio','premiere','episodes','genre','theme','image','description',)


class RelatedToSerializer(serializers.ModelSerializer):
    manga=serializers.CharField(source='manga.title.original_name',default='',read_only=True)
    anime=serializers.CharField(source='anime.title.original_name',default='',read_only=True)
    class Meta:
        model=Related
        fields=('manga','anime')
class PostSerializer(serializers.ModelSerializer):
    related_to=RelatedToSerializer()
    author=serializers.CharField(source='author.username',default='',read_only=True)
    class Meta:
        model=Post
        fields=('id','title','main_image','related_to','author','publish','created','updated','status')