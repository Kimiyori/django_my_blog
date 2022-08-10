from decimal import Decimal
from django.test import TransactionTestCase
from ..tasks import add_score, update_scores, CustomError
from ..models import *
from django.test import override_settings
from django.apps import apps


class SetScoreTaskTestCase(object):

    def setUp(self) -> None:
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra', russian_name='первый тест', english_name='first test')
        self.urls = Urls.objects.create(mal=self.right_url)

        self.modeltype = apps.get_model(app_label='titles',
                                        model_name=self.model)

        self.item = self.modeltype.objects.create(
            title=self.title,
            urls=self.urls)

    def test_success(self):
        task = add_score.delay(id=self.item.id, type=self.model)
        self.assertTrue(task.successful())
        self.item.refresh_from_db()
        self.assertEqual(self.item.score, Decimal(
            task.get()).quantize(Decimal(10) ** -2))

    def test_wrong_type(self):
        task = add_score.delay(id=self.item.id, type='something wrong')
        self.assertTrue(isinstance(task.result, ValueError))

    def test_wrong_id(self):
        task = add_score.delay(id=12345, type=self.model)
        self.assertTrue(isinstance(task.result, ValueError))

    def test_wrong_type2(self):
        opposite_type = 'anime' if self.model == 'manga' else 'manga'
        task = add_score.delay(id=self.item.id, type=opposite_type)
        self.assertTrue(isinstance(task.result, ValueError))

    def test_wrong_url(self):
        urls = Urls.objects.create(mal=self.wrong_url)
        item = self.modeltype.objects.create(
            title=self.title,
            urls=urls)
        task = add_score.delay(id=item.id, type=self.model)
        self.assertTrue(isinstance(task.result, IndexError))

    def test_not_have_url(self):
        item = self.modeltype.objects.create(
            title=self.title)
        task = add_score.delay(id=item.id, type=self.model)
        self.assertTrue(isinstance(task.result, AttributeError))

    def test_already_has_score(self):
        item = self.modeltype.objects.create(
            title=self.title,
            score=3.33,
            urls=self.urls)
        task = add_score.delay(id=item.id, type=self.model)
        self.assertTrue(isinstance(task.result, CustomError))


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
class MangaSetScoreTaskTestCase(SetScoreTaskTestCase, TransactionTestCase):

    def setUp(self) -> None:
        self.model = 'manga'
        self.right_url = 'https://myanimelist.net/manga/19896/'
        self.wrong_url = 'https://myanimeliuppswrongst.net/manga/19896/'
        super().setUp()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
class AnimeSetScoreTaskTestCase(SetScoreTaskTestCase, TransactionTestCase):

    def setUp(self) -> None:
        self.model = 'anime'
        self.right_url = 'https://myanimelist.net/anime/49521/'
        self.wrong_url = 'https://myanimewrongurllist.net/anime/49521/'
        super().setUp()


class UpdateScoresTaskTestCase(object):

    def setUp(self) -> None:
        self.title = Title.objects.create(
            original_name='Tetsugaka Letra',
            russian_name='первый тест',
            english_name='first test'
        )

        self.urls1 = Urls.objects.create(mal=self.list_right_urls[0])
        self.urls2 = Urls.objects.create(mal=self.list_right_urls[1])
        self.modeltype = apps.get_model(app_label='titles',
                                        model_name=self.model)

        self.item1 = self.modeltype.objects.create(
            title=self.title,
            urls=self.urls1)
        self.item2 = self.modeltype.objects.create(
            title=self.title,
            urls=self.urls2)

    def test_success(self):
        task = update_scores.delay(type=self.model)
        self.assertTrue(task.successful())
        self.item1.refresh_from_db()
        self.item2.refresh_from_db()
        self.assertEqual(len(task.get()), 2)
        self.assertEqual(self.item1.score, Decimal(
            task.get()[0].score).quantize(Decimal(10) ** -2))
        self.assertEqual(self.item2.score, Decimal(
            task.get()[1].score).quantize(Decimal(10) ** -2))

    def test_incorrect_type(self):
        task = update_scores.delay(type='Wrong type')
        self.assertTrue(isinstance(task.result, ValueError))

    def test_wrong_url(self):
        self.urls3 = Urls.objects.create(mal=self.wrong_url)
        self.item3 = self.modeltype.objects.create(
            title=self.title,
            urls=self.urls3)
        task = update_scores.delay(type=self.model)
        self.item3.refresh_from_db()
        self.assertEqual(len(task.get()), 2)
        self.assertEqual(self.item3.score, None)

    def test_does_not_have_url(self):
        self.item4 = self.modeltype.objects.create(
            title=self.title,)
        task = update_scores.delay(type=self.model)
        self.item4.refresh_from_db()
        self.assertEqual(len(task.get()), 2)
        self.assertEqual(self.item4.score, None)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
class AnimeUpdateScoresTaskTestCase(UpdateScoresTaskTestCase, TransactionTestCase):

    def setUp(self) -> None:
        self.model = 'anime'
        self.list_right_urls: list[str] = ['https://myanimelist.net/anime/11433/',
                                           'https://myanimelist.net/anime/22789/', ]
        self.wrong_url = 'https://myaniwrongurlmelist.net/anime/11433/'
        super().setUp()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True)
class MangaUpdateScoresTaskTestCase(UpdateScoresTaskTestCase, TransactionTestCase):

    def setUp(self) -> None:
        self.model = 'manga'
        self.list_right_urls: list[str] = ['https://myanimelist.net/manga/121727/',
                                           'https://myanimelist.net/manga/24705/', ]
        self.wrong_url = 'https://myanimwrongurlelist.net/manga/24705/'
        super().setUp()