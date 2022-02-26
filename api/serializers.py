# posts/serializers.py
from rest_framework import serializers
from anime.models import Anime
from manga.models import Title,Manga,Author,Publisher,Demographic,MangaType,Genre

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['anime','original_name', 'english_name', 'russian_name']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name','surname','photo']



class DemographicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demographic
        fields = ['name']


class MangaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MangaType
        fields = ['name']
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class MangaSerializer(serializers.ModelSerializer):
    author=AuthorSerializer()
    publisher=serializers.StringRelatedField(many=True)
    genres=serializers.StringRelatedField(many=True)
    themes=serializers.StringRelatedField(many=True)
    magazine=serializers.StringRelatedField(many=True)
    demographic=serializers.StringRelatedField()
    type=serializers.StringRelatedField()
    item  = TitleSerializer()
    class Meta:
        model = Manga
        fields = ['id','type','author','publisher','premiere','volumes','chapters','genres','demographic','themes','image','magazine','description','item']
    
 
    def update(self, instance, validated_data):
        item_manga=validated_data.pop('item')
        item_manga2=item_manga.get('anime')
        instance.item.anime=item_manga2
        instance.item.save()
        return instance

class AnimeSerializer(serializers.ModelSerializer):
    item  = TitleSerializer()
    source=MangaSerializer()
    author=AuthorSerializer()
    genres=serializers.StringRelatedField(many=True)
    themes=serializers.StringRelatedField(many=True)
    type=serializers.StringRelatedField()
    studio=serializers.StringRelatedField(many=True)

    class Meta:
        model = Anime
        fields = ('id','source','type', 'author', 'studio','premiere','episodes','genres','themes','image','description','item')

        def update(self, instance, validated_data):
            source=validated_data.pop('source')
            source_item=source.pop('item')
            print(validated_data)
            return instance
