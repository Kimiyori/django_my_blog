import uuid
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from titles.tasks import add_score
from .models import (
    Demographic,
    Urls,
    Genre,
    MangaType,
    Publisher,
    Manga,
    Theme,
    Title,
    Magazine,
    Anime,
    Studio,
    AnimeType,
    Adaptation,
    AdaptationReverse,
    SequelPrequelAnime,
    SequelPrequelManga,
    Authors,
    AuthorTable,
    Image,
)

# Register your models here.


class AdaptationInline(admin.TabularInline):
    model = Adaptation
    autocomplete_fields = ["adaptation", "based_on"]
    extra = 1


class AdaptationReverseInline(admin.TabularInline):
    model = AdaptationReverse
    autocomplete_fields = ["adaptation", "based_on"]
    extra = 1


class PrequelAnimeInline(admin.TabularInline):
    model = SequelPrequelAnime
    autocomplete_fields = ["prequel"]
    fk_name = "sequel"
    extra = 1


class SequelAnimeInline(admin.TabularInline):
    model = SequelPrequelAnime
    autocomplete_fields = ["sequel"]
    fk_name = "prequel"
    extra = 1


class PrequelMangaInline(admin.TabularInline):
    model = SequelPrequelManga
    autocomplete_fields = ["prequel"]
    fk_name = "sequel"
    extra = 1


class SequelMangaInline(admin.TabularInline):
    model = SequelPrequelManga
    autocomplete_fields = ["sequel"]
    fk_name = "prequel"
    extra = 1


@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    inlines = [
        AdaptationInline,
        AdaptationReverseInline,
        PrequelAnimeInline,
        SequelAnimeInline,
    ]
    filter_horizontal = ["genre", "studio", "theme", "related_post"]
    autocomplete_fields = [
        "title",
        "type",
    ]
    search_fields = [
        "title__original_name",
        "title__russian_name",
        "title__english_name",
    ]
    change_form_template = "admin/anime/change_form.html"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("title")

    def save_model(self, request, obj, form, change):
        add_score.delay(obj.id, "anime")
        super().save_model(request, obj, form, change)


@admin.register(AnimeType)
class AnimeTypeAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Demographic)
class DemoAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Urls)
class UrlsAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    search_fields = ["id"]


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(AuthorTable)
class AuthorTableAdmin(admin.ModelAdmin):
    prepopulated_fields = {"pseudonym": ("name",)}
    search_fields = ["name"]


@admin.register(Authors)
class AuthorsAdmin(admin.ModelAdmin):
    autocomplete_fields = [
        "author",
        "artist",
    ]
    search_fields = [
        "author",
        "artist",
    ]


@admin.register(MangaType)
class MangaTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    search_fields = ["original_name", "english_name", "russian_name"]


@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    inlines = [
        AdaptationInline,
        AdaptationReverseInline,
        SequelMangaInline,
        PrequelMangaInline,
    ]
    filter_horizontal = ["genre", "publisher", "magazine", "theme", "related_post"]
    search_fields = [
        "title__original_name",
        "title__russian_name",
        "title__english_name",
    ]
    autocomplete_fields = ["title", "type", "authors", "demographic"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("title")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        add_score.delay(obj.id, "manga")


@admin.register(Magazine)
class MagazineAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
