import random
from django.core.management.base import BaseCommand
from faker import Faker
import faker.providers
from ...models import Adaptation, AdaptationReverse, Anime, AnimeType, AuthorTable, Authors, Genre, Demographic, Magazine, Manga, MangaType, Publisher, SequelPrequelAnime, SequelPrequelManga, Theme, Studio, Title
from ...models import Image as ImageModel
from django.db import transaction
from django.db.models import Max, Min
from config import settings
import os
from django.core.files.base import ContentFile

GENRES = [
    'Tragedy',
    'Sports',
    'Slice of Life',
    'Sci-Fi',
    'Romance',
    'Psychological',
    'Mystery',
    'Mecha',
    'Magical Girls',
    'Isekai',
    'Horror',
    'Historical',
    'Fantasy',
    'Drama',
    'Crime',
    'Comedy',
    'Adventure',
    'Action'
]

DEMOGRAPHICS = [
    'Shounen',
    'Shoujo',
    'Seinen',
    'Josei',
    'Kodomomuke',

]

MAGAZINES = [
    'Afternoon',
    'Shounen Gangan',
    'Gangan Online',
    'Gangan Powered',
    'Gessan',
    'Young Sunday',
    'Comic @ Bunch',
    'Naver Webtoon',
    'Gekkan Action',
    'good! Afternoon',
    'Weekly Morning',
    'Monthly Shōnen Magazine',
    'Weekly Young Magazine',
    'Weekly Young Jump',
    'CoroCoro Comic',
    'Weekly Shōnen Magazine',
    'Weekly Shōnen Jump',
    'Shonen Jump',
]

MANGATYPE = [
    'Manhva',
    'Manhua',
    'Manga'
]

ANIMETYPE = [
    'TV Show',
    'Special',
    'OVA',
    'ONA',
    'Movie',
    'Clip',
]

PUBLISHERS = [
    'Square Enix',
    'Shueisha',
    'Shogakukan',
    'Shinchosha',
    'Naver',
    'Kodansha',
    'Kadokawa Shoten',
    'Futabasha',
    'Core Magazine'
]

THEMES = [
    'Historical',
    'Iyashikei',
    'Office Workers',
    'Survival',
    'Supernatural',
    'Music',
    'Monsters',
    'Military',
    'Magic',
    'Harem',
    'Gyaru',
    'Genderswap',
    'Cooking',
    'School',
]

STUDIOS = [
    'Wit Studio',
    'Ufotable',
    'TMS Entertainment',
    'Sunrise',
    'Studio Pierrot',
    'Studio Deen',
    'Production I.G',
    'OLM',
    'MAPPA',
    'Madhouse',
    'Kyoto Animation',
    'Kinema Citrus',
    'J.C.Staff',
    'Gonzo',
    'CoMix Wave Films',
    'Bones',
    'Artland',
    'A-1 Pictures',
]

NAMEDB = 'test_db'

NUMBER_MANGA = 500

NUMBER_ANIME = 500

NUMBER_ADAPTATION = 400

NUMBER_ADAPTATIONREVERSE =  400

NUMBER_SEQUELPREQUEL = 400
NUMBER_PREQUELSEQUEL = 400

NUMBER_POST=50

class Provider(faker.providers.BaseProvider):
    def genre(self):
        return self.random_element(GENRES)

    def demographic(self):
        return self.random_element(DEMOGRAPHICS)

    def magazine(self):
        return self.random_element(MAGAZINES)

    def manga_type(self):
        return self.random_element(MANGATYPE)

    def publisher(self):
        return self.random_element(PUBLISHERS)

    def theme(self):
        return self.random_element(THEMES)

    def studio(self):
        return self.random_element(STUDIOS)

    def anime_type(self):
        return self.random_element(ANIMETYPE)


class Command(BaseCommand):
    help = 'create data for titles model'

    def create_default_data(self):
        fake = Faker()
        fake.add_provider(Provider)
        for _ in range(len(GENRES)):
            Genre.objects.create(name=fake.unique.genre())

        for _ in range(len(DEMOGRAPHICS)):
            Demographic.objects.create(
                name=fake.unique.demographic())

        for _ in range(len(MAGAZINES)):
            Magazine.objects.create(
                name=fake.unique.magazine())

        for _ in range(len(MANGATYPE)):
            MangaType.objects.create(
                name=fake.unique.manga_type())

        for _ in range(len(PUBLISHERS)):
            Publisher.objects.create(
                name=fake.unique.publisher())

        for _ in range(len(THEMES)):
            Theme.objects.create(name=fake.unique.theme())

        for _ in range(len(STUDIOS)):
            Studio.objects.create(name=fake.unique.studio())

        for _ in range(len(ANIMETYPE)):
            AnimeType.objects.create(
                name=fake.unique.anime_type())

    def get_rand(self, model, number):
        pk = random.randint(0, number-1)
        return model.objects.all()[pk]

    def make_image(self):
        """
            Create image file
                The return value is the name of the file
        """
        file = settings.MEDIA_ROOT+'test_db/image'
        files = os.listdir(file)
        name_img = random.choices(files)
        img_path = file+'/'+name_img[0]
        img = ImageModel.objects.create()
        with open(img_path, 'rb') as f:
            data = f.read()
            img.image.save(name_img[0], ContentFile(data), save=True)
        return img

    def create_manga(self, fake):
        for _ in range(NUMBER_MANGA):
            title_original_name = fake['en-US'].sentence(nb_words=8,)
            title_english_name = fake['en-US'].sentence(nb_words=8,)
            title_russian_name = fake['ru-RU'].sentence(nb_words=8,)
            title = Title.objects.create(original_name=title_original_name,
                                                          english_name=title_english_name,
                                                          russian_name=title_russian_name)

            manga_type = self.get_rand(MangaType, len(MANGATYPE))

            author = AuthorTable.objects.create(name=fake['ja-JP'].romanized_name(),
                                                                 pseudonym=fake['ja-JP'].romanized_name(
            ),
                photo=fake['ja-JP'].image_url())
            artist = AuthorTable.objects.create(name=fake['ja-JP'].romanized_name(),
                                                                 pseudonym=fake['ja-JP'].romanized_name(
            ),
                photo=fake['ja-JP'].image_url())
            authors = Authors.objects.create(
                author=author, artist=artist)
            premiere = fake.date_object()
            volumes = random.randint(1, 100)
            chapters = random.randint(volumes, volumes*6)
            description = fake['en-US'].text(max_nb_chars=350)
            manga = Manga.objects.create(title=title, type=manga_type,
                                                          authors=authors, premiere=premiere,
                                                          volumes=volumes, chapters=chapters,
                                                          image=self.make_image(), description=description)
            publishers = random.sample(
                list(Publisher.objects.all()), random.randint(1, 3))
            manga.publisher.add(*publishers)
            themes = random.sample(list(Theme.objects.all()), random.randint(1, 3))
            manga.theme.add(*themes)
            magazines = random.sample(
                list(Magazine.objects.all()), random.randint(1, 3))
            manga.magazine.add(*magazines)
            genres = random.sample(list(Genre.objects.all()), random.randint(1, 3))
            manga.genre.add(*genres)

    def create_anime(self, fake):
        for _ in range(NUMBER_ANIME):
            title_original_name = fake['en-US'].sentence(nb_words=8,)
            title_english_name = fake['en-US'].sentence(nb_words=8,)
            title_russian_name = fake['ru-RU'].sentence(nb_words=8,)
            title = Title.objects.create(original_name=title_original_name,
                                                          english_name=title_english_name,
                                                          russian_name=title_russian_name)

            anime_type = self.get_rand(AnimeType, len(ANIMETYPE))

            premiere = fake.date_object()

            episodes = random.randint(1, 100)

            description = fake['en-US'].text(max_nb_chars=350)
            anime = Anime.objects.create(title=title, type=anime_type,
                                                          premiere=premiere,
                                                          episodes=episodes,
                                                          image=self.make_image(), description=description)
            studios = random.sample(
                list(Studio.objects.all()), random.randint(1, 3))
            anime.studio.add(*studios)
            themes = random.sample(list(Theme.objects.all()), random.randint(1, 3))
            anime.theme.add(*themes)
            genres = random.sample(list(Genre.objects.all()), random.randint(1, 3))
            anime.genre.add(*genres)

    def create_adaptations(self, fake):
        for _ in range(NUMBER_ADAPTATION):

            manga = self.get_rand(Manga, NUMBER_MANGA)
            anime = self.get_rand(Anime, NUMBER_ANIME)
            Adaptation.objects.create(
                adaptation=anime, based_on=manga)

    def create_reverse_adaptations(self, fake):
        for _ in range(NUMBER_ADAPTATIONREVERSE):
            manga = self.get_rand(Manga, NUMBER_MANGA)
            anime = self.get_rand(Anime, NUMBER_ANIME)
            AdaptationReverse.objects.create(
                adaptation=manga, based_on=anime)

    def create_sequel_prequel(self, fake):
        for _ in range(NUMBER_SEQUELPREQUEL):
            anime1 = self.get_rand(Anime, NUMBER_ANIME)
            anime2 = self.get_rand(Anime, NUMBER_ANIME)
            SequelPrequelAnime.objects.create(
                sequel=anime1, prequel=anime2)

    def create_prequel_sequel(self, fake):
        for _ in range(NUMBER_PREQUELSEQUEL):
            manga1 = self.get_rand(Manga, NUMBER_MANGA)
            manga2 = self.get_rand(Manga, NUMBER_MANGA)
            SequelPrequelManga.objects.create(
                sequel=manga1, prequel=manga2)



    def delete_all_data(self, models):
        for m in models:
            m.objects.all().delete()

    @transaction.atomic
    def handle(self, *args, **kwargs):
        locale_list = ['en-US', 'ja-JP', 'ru_RU']
        fake = Faker(locale_list)

        models = [Adaptation, AdaptationReverse, Anime, AnimeType, AuthorTable, Authors, Genre, Demographic, Magazine,
                  Manga, MangaType, Publisher, SequelPrequelAnime, SequelPrequelManga, Theme, Studio, Title, ImageModel]

        self.delete_all_data(models)

        self.create_default_data()

        self.create_manga(fake)

        self.create_anime(fake)

        self.create_adaptations(fake)

        self.create_reverse_adaptations(fake)

        self.create_sequel_prequel(fake)

        self.create_prequel_sequel(fake)


