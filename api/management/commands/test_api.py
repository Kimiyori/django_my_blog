import requests
from rest_framework.test import APIClient
from django.core.management.base import BaseCommand
from django.test import Client
import json
class Command(BaseCommand):


    def handle(self, *args, **kwargs):
 
        data={
   "volumes":12,
   "chapters":35
}
        factory = APIClient()
        factory.login(username='Kimiyori', password='maxmax17')
        response = factory.patch(
            'http://127.0.0.1:8000/api/manga/79cc475c-87a1-4c7e-865d-1f83e2553846/', 
            data=data,
             format='json')
        print(response)
