from ...models import *

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404, get_object_or_404
from django.core.paginator import Paginator


from django.http import HttpResponse
import requests
import time

from django.db import models
from django.utils import timezone

import os

from datetime import datetime

from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from datetime import datetime
from django.contrib import messages
import random
import string
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

import random
import string

import base64

import time
from django.http import JsonResponse

import re
import json

from django.conf import settings
from django.db.models import Q

import datetime

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


import base64



    
def product_admin(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        context['list_Product'] = Product.objects.all()
        s = request.GET.get('s')
        if s:
            context['list_Product'] = context['list_Product'].filter(Q(Title__icontains=s)).order_by('-id')
            context['s'] = s
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/product_admin.html', context, status=200)
        else:
            return redirect('login_admin')
        

def product_add_admin(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/product_add_admin.html', context, status=200)
        else:
            return redirect('login_admin')
        
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Title'] = request.POST.get('Title')
            fields['Description'] = request.POST.get('Description')
            fields['Avatar']= request.FILES.get('Avatar')
            fields['Link'] = request.POST.get('Link')
            fields['Iframe'] = request.POST.get('Iframe')
            fields['Video']= request.FILES.get('Video')
            obj = Product.objects.create(**fields)
            return redirect('product_admin')
        else:
            return redirect('login_admin')
    
def product_edit_admin(request,pk):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        context['obj_Product'] = Product.objects.get(pk=pk)
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/product_edit_admin.html', context, status=200)
        else:
            return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Title'] = request.POST.get('Title')
            fields['Description'] = request.POST.get('Description')
            fields['Avatar']= request.FILES.get('Avatar')
            fields['Link'] = request.POST.get('Link')
            fields['Iframe'] = request.POST.get('Iframe')
            fields['Video']= request.FILES.get('Video')

            obj = Product.objects.get(pk=pk)
            obj.Title = fields['Title']
            obj.Description = fields['Description']
            obj.Link = fields['Link']
            obj.Iframe = fields['Iframe']
            if fields['Avatar']:
                if obj.Avatar:   # nếu đã có file cũ
                    obj.Avatar.delete(save=False)  # xoá file cũ trong media
                obj.Avatar = fields['Avatar']

            if fields['Video']:
                if obj.Video:
                    obj.Video.delete(save=False)
                obj.Video = fields['Video']

            obj.save()
            return redirect('product_edit_admin',pk=pk)
        else:
            return redirect('login_admin')
    
def product_remove_admin(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            try:
                obj = Product.objects.get(pk=pk)
                # Xoá Avatar file nếu tồn tại
                if obj.Avatar:   # nếu đã có file cũ
                    obj.Avatar.delete(save=False)  # xoá file cũ trong media
                if obj.Video:
                    obj.Video.delete(save=False)
                obj.delete()
            except:
                print('not')
            return redirect('product_admin')
    else:
        return redirect('login_admin')
        

