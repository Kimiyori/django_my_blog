# posts/serializers.
from django.apps import apps

from requests import post
from post.models import Post
from rest_framework import serializers
import logging
from titles.models import Anime, Magazine, Theme, Title, Manga, AuthorTable, Publisher, Demographic, MangaType, Genre, Authors, AuthorTable, Image
logging.basicConfig(format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ['original_name', 'english_name', 'russian_name']
    
    def update(self, instance, validated_data): 
        logger.info(f'Starting update instance of title model with folloving fields:{*[x for x in validated_data.keys()],}')
        instance.original_name=validated_data.pop('original_name',instance.original_name)
        instance.english_name=validated_data.pop('english_name',instance.english_name)
        instance.russian_name=validated_data.pop('russian_name',instance.russian_name)
        instance.save()
        logger.info('Successful update instance of item model')
        return instance


class AuthorTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorTable
        fields = ['name', 'photo']


class AuthorsSerializer(serializers.ModelSerializer):
    author = AuthorTableSerializer()

    artist = AuthorTableSerializer()

    class Meta:
        model = Authors
        fields = ['author', 'artist']

    def update(self, instance, validated_data):

        author = AuthorTableSerializer(
            instance=instance.author, data=validated_data.pop('author',instance.author))
        if author.is_valid():
            author.save()
        artist = AuthorTableSerializer(
            instance=instance.artist, data=validated_data.pop('artist',instance.artist))
        if artist.is_valid():
            artist.save()
        return instance


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image', 'thumbnail']


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ['name']
 

class MangaSerializer(serializers.Serializer):
    id=serializers.UUIDField(read_only=True)
    premiere=serializers.DateField(required=False)
    volumes=serializers.IntegerField(required=False)
    chapters=serializers.IntegerField(required=False)
    authors = AuthorsSerializer(required=False)
    publisher = serializers.SlugRelatedField(queryset=Publisher.objects.all(), many=True,slug_field='name',required=False)
    genre = serializers.SlugRelatedField(queryset=Genre.objects.all(), many=True,slug_field='name',required=False)
    theme = serializers.SlugRelatedField(queryset=Theme.objects.all(), many=True,slug_field='name',required=False)
    magazine = serializers.SlugRelatedField(queryset=Magazine.objects.all(), many=True,slug_field='name',required=False)
    demographic = serializers.SlugRelatedField(queryset=Demographic.objects.all(),slug_field='name',required=False)
    type = serializers.PrimaryKeyRelatedField(queryset=MangaType.objects.all(),required=False)
    title = TitleSerializer()
    image = ImageSerializer(required=False)
    related_post = serializers.HyperlinkedIdentityField(
        many=True, view_name='post_detail', format='html',required=False)
    description=serializers.CharField(required=False)


    def get_values(self, field, data):
        model=apps.get_model(app_label='titles',model_name=field)
        obj = model.objects.filter(name__in=data).values_list('id',flat=True)
        return obj

    def create(self, validated_data):

        logger.info(f'Starting create instance of manga model with folloving fields:{*[x for x in validated_data.keys()],}')
        

        logger.info('Successful create instance of manga model')
       


    def update(self, instance, validated_data):  
        
        logger.info(f'Starting update instance of manga model with folloving fields:{*[x for x in validated_data.keys()],}')
        # default fields
        fields=[ 'type',  'premiere',
                  'volumes', 'chapters',  'demographic',
                 'description', ]
        for field in fields:
            try:
                data=validated_data.pop(field,getattr(instance,field))
                if data:
                    setattr(instance,field,data)
            except KeyError as e:  # validated_data may not contain all fields during HTTP PATCH
                   logger.warning(e)
        

        #manytomant fields
        manytomany_fields=['genre','theme','publisher','magazine']
        for field in manytomany_fields:
            try:
                data = validated_data.pop(field, [])
                if data:
                    field_instance=getattr(instance,field)
                    field_instance.set(self.get_values(field=field,data=data))
            except Exception as e:
                logger.warning(e)

        #nested fields
        nested_fields={'title':TitleSerializer,'authors':AuthorsSerializer,'image':ImageSerializer}
        for field,serializer in nested_fields.items():
            try:
                get_field=getattr(instance,field)
                data=validated_data.pop(field,None)
                if data:
                    obj=serializer(instance=get_field,data=data)
                    if obj.is_valid():
                        obj.save()
            except Exception as e:
                logger.warning(e)

        instance.save()

        logger.info('Successful update instance of manga model')
        return instance


class AnimeSerializer(serializers.ModelSerializer):
    title = TitleSerializer()
    genre = serializers.StringRelatedField(many=True)
    theme = serializers.StringRelatedField(many=True)
    type = serializers.StringRelatedField()
    studio = serializers.StringRelatedField(many=True)
    image = ImageSerializer()

    class Meta:
        model = Anime
        fields = ('id', 'title', 'type', 'studio', 'premiere',
                  'episodes', 'genre', 'theme', 'image', 'description',)


class PostSerializer(serializers.ModelSerializer):

    author = serializers.CharField(
        source='author.username', default='', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'main_image', 'related_to',
                  'author', 'publish', 'created', 'updated', 'status')
