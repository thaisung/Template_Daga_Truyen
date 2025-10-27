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



    
def odds_admin(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        context['list_Odds'] = Odds.objects.all()
        s = request.GET.get('s')
        if s:
            context['list_Odds'] = context['list_Odds'].filter(Q(Title__icontains=s)).order_by('-id')
            context['s'] = s
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/odds_admin.html', context, status=200)
        else:
            return redirect('login_admin')
        

def odds_add_admin(request):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Category'] = request.POST.get('Category')
            fields['Describe'] = request.POST.get('Describe')
            obj = Odds.objects.create(**fields)

            List_Image = request.FILES.getlist('List_Image')

            if List_Image:
                for img in List_Image:
                    img_obj = Odds_Image.objects.create(Link_image=obj,Image=img)

            return redirect('odds_admin')
        else:
            return redirect('login_admin')
    
def odds_edit_admin(request,pk):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Category'] = request.POST.get('Category')
            fields['Describe'] = request.POST.get('Describe')

            obj = Odds.objects.get(pk=pk)

            if fields['Category']:
                obj.Category = fields['Category']
            if fields['Describe']:
                obj.Describe = fields['Describe']
            
            obj.save()

            List_Image = request.FILES.getlist('List_Image')
            List_Image_Odds = Odds_Image.objects.filter(List_Image=obj)

            # Nếu có ảnh mới upload
            if List_Image:
                # Xóa ảnh cũ
                for img_obj in List_Image_Odds:
                    if img_obj.Image:
                        img_obj.Image.delete(save=False)
                    img_obj.delete()

                # Thêm ảnh mới
                for img in List_Image:
                    Odds_Image.objects.create(Link_image=obj, Image=img)

            return redirect('odds_admin')
        else:
            return redirect('login_admin')
    
def odds_remove_admin(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            try:
                obj = Odds.objects.get(pk=pk)
                obj.delete()
            except:
                print('not')
            return redirect('odds_admin')
    else:
        return redirect('login_admin')
        

