# blog/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import *

from datetime import datetime

from .views.client.home_client import *

protocol = 'https'

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
        ]

    def location(self, item):
        return reverse(item)

    

