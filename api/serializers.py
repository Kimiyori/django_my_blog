# posts/serializers.py
from requests import post
from post.models import Post
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



class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']

class MangaSerializer(serializers.ModelSerializer):
    authors=AuthorsSerializer()
    publisher=serializers.StringRelatedField(many=True)
    genre= serializers.StringRelatedField(many=True)
    theme=serializers.StringRelatedField(many=True)
    magazine=serializers.StringRelatedField(many=True)
    demographic=serializers.StringRelatedField()
    type=serializers.StringRelatedField()
    title  = TitleSerializer()
    image=ImageSerializer()
    related_post=serializers.HyperlinkedIdentityField(many=True,view_name='post_detail', format='html')
    class Meta:
        model = Manga
        fields = ['id','title','type','authors','publisher','premiere',
                    'volumes','chapters','genre','demographic','theme',
                                    'image','magazine','description','related_post']

    def get_or_create_packages(self, packages):
        package_ids = []
        for package in packages:
            package_instance, created = Genre.objects.get_or_create(pk=package.get('id'), defaults=package)
            package_ids.append(package_instance.pk)
        return package_ids


    def create(self, validated_data):
        package = validated_data.pop('genre', [])

        order = Manga.objects.create(**validated_data)
        order.genre.set(self.get_or_create_packages(package))
        return order
    
    def update(self, instance, validated_data):

        instance.description=validated_data.pop('description',instance.description)
        instance.volumes=validated_data.pop('volumes',instance.volumes)
        instance.chapters=validated_data.pop('chapters',instance.chapters)
        instance.save()

        title= TitleSerializer(instance=instance.title,data=validated_data.pop('title'))
        if title.is_valid():
            title.save()
        
        return instance


 


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



class PostSerializer(serializers.ModelSerializer):

    author=serializers.CharField(source='author.username',default='',read_only=True)
    class Meta:
        model=Post
        fields=('id','title','main_image','related_to','author','publish','created','updated','status')