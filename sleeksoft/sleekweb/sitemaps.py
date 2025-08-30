# blog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import *

from datetime import datetime

from .views.client.home_client import *

protocol = 'https'

class VideoSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return Product.objects.all()  # trả về list Product

    def location(self, obj):
        return reverse('home', kwargs={'slug': obj.Slug})

    

