# posts/serializers.

from django.apps import apps
from django.db import transaction
from post.models import Content, File, Post, Text, Video
from post.models import Image as ImageContent
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
import logging
from titles.models import (
    Anime,
    AnimeType,
    Magazine,
    Studio,
    Theme,
    Title,
    Manga,
    AuthorTable,
    Publisher,
    Demographic,
    MangaType,
    Genre,
    Authors,
    AuthorTable,
    Image,
)
from django.contrib.auth import get_user_model

file_logger = logging.getLogger("file_logger")
console_logger = logging.getLogger("console_logger")


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ["original_name", "english_name", "russian_name"]

    @transaction.atomic
    def create(self, validated_data):
        original_name = validated_data.pop("original_name", None)
        english_name = validated_data.pop("english_name", None)
        russian_name = validated_data.pop("russian_name", None)
        title = Title.objects.create(
            original_name=original_name,
            english_name=english_name,
            russian_name=russian_name,
        )
        console_logger.info("Successful create instance of title model")
        return title

    def update(self, instance, validated_data):
        instance.original_name = validated_data.pop(
            "original_name", instance.original_name
        )
        instance.english_name = validated_data.pop(
            "english_name", instance.english_name
        )
        instance.russian_name = validated_data.pop(
            "russian_name", instance.russian_name
        )
        instance.save()
        console_logger.info("Successful update instance of title model")
        return instance


class AuthorTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorTable
        fields = ["name", "photo"]


class AuthorsSerializer(serializers.ModelSerializer):
    author = AuthorTableSerializer()

    artist = AuthorTableSerializer()

    class Meta:
        model = Authors
        fields = ["author", "artist"]

    def update(self, instance, validated_data):

        author = AuthorTableSerializer(
            instance=instance.author, data=validated_data.pop("author", instance.author)
        )
        if author.is_valid():
            author.save()
        artist = AuthorTableSerializer(
            instance=instance.artist, data=validated_data.pop("artist", instance.artist)
        )
        if artist.is_valid():
            artist.save()
        return instance


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image", "thumbnail"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = ["name"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["name"]


class DemographicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demographic
        fields = ["name"]


class MagazineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Magazine
        fields = ["name"]


class MangaSerializer(DynamicFieldsModelSerializer):
    title = TitleSerializer(required=False)
    premiere = serializers.DateField(required=False)
    volumes = serializers.IntegerField(required=False)
    chapters = serializers.IntegerField(required=False)
    authors = AuthorsSerializer(required=False)
    publisher = serializers.SlugRelatedField(
        queryset=Publisher.objects.all(), many=True, slug_field="name", required=False
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field="name", required=False
    )
    theme = serializers.SlugRelatedField(
        queryset=Theme.objects.all(), many=True, slug_field="name", required=False
    )
    magazine = serializers.SlugRelatedField(
        queryset=Magazine.objects.all(), many=True, slug_field="name", required=False
    )
    demographic = serializers.SlugRelatedField(
        queryset=Demographic.objects.all(), slug_field="name", required=False
    )
    type = serializers.SlugRelatedField(
        queryset=MangaType.objects.all(), slug_field="name", required=False
    )

    image = ImageSerializer(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = Manga
        fields = (
            "id",
            "title",
            "type",
            "publisher",
            "magazine",
            "chapters",
            "volumes",
            "genre",
            "authors",
            "theme",
            "demographic",
            "premiere",
            "image",
            "description",
        )

    def get_values(self, field, data):
        model = apps.get_model(app_label="titles", model_name=field)
        obj = model.objects.filter(name__in=data).values_list("id", flat=True)
        return obj

    @transaction.atomic
    def create(self, validated_data):
        file_logger.info(
            f"Starting create instance of manga model with folloving fields",
            extra={
                "fields": {
                    *[x for x in validated_data.keys()],
                }
            },
        )
        title = validated_data.pop("title")
        # title = Title.objects.create(**validated_data.pop('title'))

        authors = validated_data.pop("authors", None)
        if authors:
            author = authors.pop("author", None)
            if author:
                author, created = AuthorTable.objects.get_or_create(**author)
            artist = authors.pop("artist", None)
            if artist:
                artist, created = AuthorTable.objects.get_or_create(**artist)
            authors = Authors.objects.create(author=author, artist=artist)
        image = validated_data.pop("image", None)
        genre = validated_data.pop("genre", [])
        theme = validated_data.pop("theme", [])
        publisher = validated_data.pop("publisher", [])
        magazine = validated_data.pop("magazine", [])

        manga = Manga.objects.create(**validated_data)

        if authors:
            manga.authors = authors
        if title:
            title = TitleSerializer(data=title)
            if title.is_valid():
                title = title.save()
                manga.title = title
        manga.genre.set(genre)
        manga.theme.set(theme)
        manga.publisher.set(publisher)
        manga.magazine.set(magazine)
        if image:

            image = Image.objects.create(**image)
            manga.image = image
        manga.save()
        file_logger.info("Successful create instance of manga model")
        return manga

    @transaction.atomic
    def update(self, instance, validated_data):

        file_logger.info(
            f"Starting update instance of manga model with folloving fields:{*[x for x in validated_data.keys()],}"
        )
        # default fields
        fields = [
            "type",
            "premiere",
            "volumes",
            "chapters",
            "demographic",
            "description",
        ]
        for field in fields:
            data = validated_data.pop(field, None)
            if data:
                setattr(instance, field, data)
        # manytomant fields
        manytomany_fields = ["genre", "theme", "publisher", "magazine"]
        for field in manytomany_fields:
            data = validated_data.pop(field, None)
            if data:
                data = (
                    list(getattr(instance, field).values_list("name", flat=True)) + data
                )
                field_instance = getattr(instance, field)
                field_instance.set(self.get_values(field=field, data=data))

        # nested fields
        nested_fields = {
            "title": TitleSerializer,
            "authors": AuthorsSerializer,
            "image": ImageSerializer,
        }
        for field, serializer in nested_fields.items():
            data = validated_data.pop(field, None)
            if data:
                get_field = getattr(instance, field)
                obj = serializer(instance=get_field, data=data)
                if obj.is_valid():
                    obj.save()
        instance.save()

        file_logger.info("Successful update instance of manga model")
        return instance


class AnimeSerializer(DynamicFieldsModelSerializer):
    title = TitleSerializer(required=False)
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), many=True, slug_field="name", required=False
    )
    theme = serializers.SlugRelatedField(
        queryset=Theme.objects.all(), many=True, slug_field="name", required=False
    )
    type = serializers.SlugRelatedField(
        queryset=AnimeType.objects.all(), slug_field="name", required=False
    )
    studio = serializers.SlugRelatedField(
        queryset=Studio.objects.all(), many=True, slug_field="name", required=False
    )
    image = ImageSerializer(required=False)

    class Meta:
        model = Anime
        fields = (
            "id",
            "title",
            "type",
            "studio",
            "premiere",
            "episodes",
            "genre",
            "theme",
            "image",
            "description",
        )

    def get_values(self, field, data):
        model = apps.get_model(app_label="titles", model_name=field)
        obj = model.objects.filter(name__in=data).values_list("id", flat=True)
        return obj

    @transaction.atomic
    def create(self, validated_data):
        file_logger.info(
            f"Starting create instance of anime model with folloving fields",
            extra={
                "fields": {
                    *[x for x in validated_data.keys()],
                }
            },
        )
        title = validated_data.pop("title")
        image = validated_data.pop("image", None)
        genre = validated_data.pop("genre", [])
        theme = validated_data.pop("theme", [])
        studio = validated_data.pop("studio", [])
        anime = Anime.objects.create(**validated_data)

        if title:
            title = TitleSerializer(data=title)
            if title.is_valid():
                title = title.save()
                anime.title = title
        anime.genre.set(genre)
        anime.theme.set(theme)
        anime.studio.set(studio)

        if image:
            image = Image.objects.create(**image)
            anime.image = image
        anime.save()
        file_logger.info("Successful create instance of anime model")
        return anime

    @transaction.atomic
    def update(self, instance, validated_data):

        console_logger.info(
            f"Starting update instance of anime model with following fields:",
            extra={
                "fields": {
                    *[x for x in validated_data.keys()],
                }
            },
        )
        # default fields
        fields = [
            "type",
            "premiere",
            "episodes",
            "description",
        ]
        for field in fields:
            data = validated_data.pop(field, None)
            if data:
                setattr(instance, field, data)
        # manytomant fields
        manytomany_fields = ["genre", "theme", "studio"]
        for field in manytomany_fields:
            data = validated_data.pop(field, None)
            if data:
                data = (
                    list(getattr(instance, field).values_list("name", flat=True)) + data
                )
                field_instance = getattr(instance, field)
                field_instance.set(self.get_values(field=field, data=data))
        # nested fields
        nested_fields = {"title": TitleSerializer, "image": ImageSerializer}
        for field, serializer in nested_fields.items():
            data = validated_data.pop(field, None)
            if data:
                get_field = getattr(instance, field)
                obj = serializer(instance=get_field, data=data)
                if obj.is_valid():
                    obj.save()

        instance.save()

        file_logger.info("Successful update instance of anime model")
        return instance


class TextSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="text")

    class Meta:
        model = Text
        fields = ("created", "updated", "item")


class ImageSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="image")

    class Meta:
        model = ImageContent
        fields = ("created", "updated", "item")


class VideoSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="video")

    class Meta:
        model = Video
        fields = ("created", "updated", "item")


class FileSerializer(serializers.ModelSerializer):
    item = serializers.CharField(source="file")

    class Meta:
        model = File
        fields = ("created", "updated", "item")


class GenericRelateField(serializers.RelatedField):
    def to_representation(self, value):
        """
        Serialize tagged objects to a simple textual representation.
        """
        if isinstance(value, Text):
            serializer = TextSerializer(value)
        elif isinstance(value, ImageContent):
            serializer = ImageSerializer(value)
        elif isinstance(value, Video):
            serializer = VideoSerializer(value)
        elif isinstance(value, File):
            serializer = FileSerializer(value)
        return serializer.data


class ContentSerializer(serializers.ModelSerializer):
    content = GenericRelateField(source="item", read_only=True)
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field="model",
    )

    class Meta:
        model = Content
        fields = (
            "order",
            "content_type",
            "content",
        )


class UserSerializator(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        # model=get_user_model()
        fields = ("id", "username")


class PostSerializer(DynamicFieldsModelSerializer):
    author = UserSerializator()
    contents = ContentSerializer(many=True, required=False)
    count_contents = serializers.IntegerField(source="contents.count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "main_image",
            "author",
            "publish",
            "created",
            "updated",
            "status",
            "count_contents",
            "contents",
        )
