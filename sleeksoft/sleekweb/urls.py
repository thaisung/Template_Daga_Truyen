"""
URL configuration for luanvan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.contrib import admin
# from Data_Interaction.admin import admin_site
from django.urls import path

from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from django.urls import re_path,path


from django.views.generic.base import TemplateView
from django.conf.urls.static import serve

from django.views.generic import RedirectView

from django.contrib.auth import views as auth_views


from .views.client.home_client import *

from .views.client.about_client import *
from .views.client.booking_client import *
from .views.client.contact_client import *
from .views.client.menu_client import *
from .views.client.service_client import *
from .views.client.team_client import *
from .views.client.testimonial_client import *


from .views.client.login_client import *
from sleekweb.sitemaps import *
from django.contrib.sitemaps.views import sitemap

from .views.admin.login_admin import *
from .views.admin.product_admin import *
from .views.admin.ads_admin import *


sitemaps_dict = {
    'static': VideoSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='sitemap'),

    path('set-language/<str:lang_code>/', set_language, name='set_language'),

    path('video/<str:slug>',home,name='home'),

    path('about',about,name='about'),
    path('booking',booking,name='booking'),
    path('contact',contact,name='contact'),
    path('menu',menu,name='menu'),
    path('service',service,name='service'),
    path('team',team,name='team'),
    path('testimonial',testimonial,name='testimonial'),


    path('admin/login', login_admin,name='login_admin'),
    path('admin/logout', logout_admin,name='logout_admin'),

    path('admin/product', product_admin,name='product_admin'),
    path('admin/product/add', product_add_admin,name='product_add_admin'),
    path('admin/product/edit/<int:pk>/', product_edit_admin,name='product_edit_admin'),
    path('admin/product/remove/<int:pk>/', product_remove_admin,name='product_remove_admin'),

    path('admin/ads', ads_admin,name='ads_admin'),
    path('admin/ads/add', ads_add_admin,name='ads_add_admin'),
    path('admin/ads/edit/', ads_edit_admin,name='ads_edit_admin'),
    path('admin/ads/remove/<int:pk>/', ads_remove_admin,name='ads_remove_admin'),





]