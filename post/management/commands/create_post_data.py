import random
from django.core.management.base import BaseCommand
from faker import Faker
from ...models import Post,Content
from titles.models import Image as ImageModel
from titles.models import Anime, Manga
from titles.management.commands.create_titles_data import NUMBER_ANIME, NUMBER_MANGA
from django.db import transaction
from django.db.models import Max, Min
from config import settings
import os
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.apps import apps

NUMBER_POST = 50

NUMBER_USERS = 10

VIDEO_URLS=[
    'https://www.youtube.com/watch?v=z5Dhxw0SeMs&list=RDz5Dhxw0SeMs&start_radio=1&ab_channel=EvanCall-Topic',
    'https://www.youtube.com/watch?v=KPxSS1zHWwQ&list=RDz5Dhxw0SeMs&index=2&ab_channel=AnimeLuna',
    'https://www.youtube.com/watch?v=8zGlL44Ov9s&list=RDGMEMCMFH2exzjBeE_zAHHJOdxg&start_radio=1&rv=KPxSS1zHWwQ&ab_channel=PhoenixKappashiro',
    'https://www.youtube.com/watch?v=VcPe2-MHXRA&list=RDGMEMCMFH2exzjBeE_zAHHJOdxg&index=5&ab_channel=HiroyukiSawano-Topic',
    'https://www.youtube.com/watch?v=EhAX68uF6NU&list=RDGMEMCMFH2exzjBeE_zAHHJOdxg&index=4&ab_channel=CHMusicChannel',
    'https://www.youtube.com/watch?v=nt4g6yMPoLE&ab_channel=S.Cloud',
    'https://www.youtube.com/watch?v=yWp6SXivHBQ&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=5&ab_channel=アニプレックスYouTubeチャンネル',
    'https://www.youtube.com/watch?v=iP3PcDNhJXI&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=31&ab_channel=ユアネス-yourness-',
    'https://www.youtube.com/watch?v=SmYco84Tvbg&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=7&ab_channel=IrohaCeleb',
    'https://www.youtube.com/watch?v=cyF1EASmETs&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=32&ab_channel=Hanfos',
    'https://www.youtube.com/watch?v=M3Y9GxRxjFM&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=6&ab_channel=HarukatoMiyuki-Topic',
    'https://www.youtube.com/watch?v=Y_7gT5v4LTM&ab_channel=TRUE-Topic',
    'https://www.youtube.com/watch?v=hVNJ-ABiXtg&ab_channel=澤野弘之%2FSawanoHiroyuki%5BnZk%5D',
    'https://www.youtube.com/watch?v=YDvLaTYlXxM&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD',
    'https://www.youtube.com/watch?v=S9Fp1M2WCyU&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=42&ab_channel=HiroyukiSawano-Topic',
    'https://www.youtube.com/watch?v=ce_9Ze-gf2o&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=75&ab_channel=miletOfficialYouTubeChannel',
    'https://www.youtube.com/watch?v=l0H1Giv57Qg&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=121&ab_channel=藍月なくる%2FAitsukiNakuru',
    'https://www.youtube.com/watch?v=msQD-mWjtyg&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=304&ab_channel=ForsakenEremith',
    'https://www.youtube.com/watch?v=zH-1T3aV6mI&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=154&ab_channel=Hakubi-Topic',
    'https://www.youtube.com/watch?v=u14WlAJ_WAI&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=120&ab_channel=暁Records',
    'https://www.youtube.com/watch?v=zBEjmMLe8Zw&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=1&ab_channel=Un3hcorn%2a.',
    'https://www.youtube.com/watch?v=q8f6y49XOhM&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=132&ab_channel=五十嵐由紀',
    'https://www.youtube.com/watch?v=Hkx1w1e5IRs&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=23&ab_channel=%28K%29NoW_NAME-Topic',
    'https://www.youtube.com/watch?v=xNRdJmB-M3I&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=123&ab_channel=FlyingDog',
    'https://www.youtube.com/watch?v=xZD1B1TskXs&list=PLBqlGO1fLIZtBkAJuncUrGQeNPLeSa5MD&index=41&ab_channel=akgVEVO',
]

class Command(BaseCommand):
    help = 'create data for post model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locale_list = ['en-US', 'ja-JP', 'ru_RU']
        self.fake = Faker(locale_list)

    def get_rand(self, model, number):
        pk = random.randint(1, number-1)
        return model.objects.all()[pk]

    def make_image(self):
        file = settings.MEDIA_ROOT+'test_db/image'
        files = os.listdir(file)
        name_img = random.choice(files)
        img_path = file+'/'+name_img
        img = ImageModel.objects.create()
        with open(img_path, 'rb') as f:
            data = f.read()
            img.image.save(name_img, ContentFile(data), save=True)
        return img

    def create_users(self):
        for _ in range(NUMBER_USERS):
            User = get_user_model()
            profile = self.fake.profile(fields=['username', 'mail'])
            user=User.objects.create(
                username=profile['username'],
                email=profile['mail'],
            )  
            user.set_password(self.fake.password(
                    length=20, special_chars=False, upper_case=False))
            user.save()

    def create_post(self):
        for _ in range(NUMBER_POST):
            title = self.fake.sentence(nb_words=8,)

            user=get_user_model()
            author = self.get_rand(user, NUMBER_USERS)
            post=Post.objects.create(
                title=title, author=author,)
            file = settings.MEDIA_ROOT+'test_db/image'
            files = os.listdir(file)
            name_img = random.choice(files)
            img_path = file+'/'+name_img
            with open(img_path, 'rb') as f:
                data = f.read()
                post.main_image.save(name_img, ContentFile(data), save=True)
            number_contents=random.randint(2,15)
            self.create_content_item(post,number_contents)

    def get_item(self,post):
        list_items=['text','image','video']
        random_item=random.choice(list_items)
        if random_item=='text':
            content=self.fake.text(max_nb_chars=500)
        elif random_item=='video':
            content=random.choice(VIDEO_URLS)
        model=apps.get_model(app_label='post',
                                  model_name=random_item)
        if random_item!='image':
            item=model.objects.create(**{'post':post,random_item:content})
        else:
            item=model.objects.create(**{'post':post,})
            file = settings.MEDIA_ROOT+'test_db/image'
            files = os.listdir(file)
            name_img = random.choice(files)
            img_path = file+'/'+name_img
            with open(img_path, 'rb') as f:
                data = f.read()
                item.image.save(name_img, ContentFile(data), save=True)
        return item


    def create_content_item(self,post,number):
        
        for x in range(1,number):
            item=self.get_item(post)
            Content.objects.create(post=post,item=item,order=x)

            

    def delete_all_data(self, models):
        for m in models:
            m.objects.all().delete()

    @transaction.atomic
    def handle(self, *args, **kwargs):


        models = [Post,Content]

        self.delete_all_data(models)

        #self.create_users()

        #self.create_post()

