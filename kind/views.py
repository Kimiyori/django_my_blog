from django.shortcuts import render
from django.views.generic import ListView,DetailView
from .models import Kind
# Create your views here.
class List(DetailView):
    model = Kind
    template_name='list.html'
    context_object_name = 'list'