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



    
def ads_admin(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        context['list_Ads'] = Ads.objects.all().order_by('Count')
        s = request.GET.get('s')
        if s:
            context['list_Ads'] = context['list_Ads'].filter(Q(Title__icontains=s)).order_by('-id')
            context['s'] = s
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/ads_admin.html', context, status=200)
        else:
            return redirect('login_admin')
        

def ads_add_admin(request):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Note'] = request.POST.get('Note')
            fields['Banner'] = request.FILES.get('Banner')
            fields['Link'] = request.POST.get('Link')
            fields['Script'] = request.POST.get('Script')
            obj = Ads.objects.create(**fields)
            return redirect('ads_admin')
        else:
            return redirect('login_admin')
    
def ads_edit_admin(request,pk):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Note'] = request.POST.get('Note')
            fields['Banner'] = request.FILES.get('Banner')
            fields['Link'] = request.POST.get('Link')
            fields['Script'] = request.POST.get('Script')

            obj = Ads.objects.get(pk=pk)

            if fields['Note']:
                obj.Note = fields['Note']
            if fields['Banner']:
                obj.Banner.delete(save=False)
                obj.Banner = fields['Banner']
            if fields['Link']:
                obj.Link = fields['Link']
                
            obj.Script = fields['Script']

            obj.save()
            return redirect('ads_admin')
        else:
            return redirect('login_admin')
    
def ads_remove_admin(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            try:
                obj = Ads.objects.get(pk=pk)
                obj.delete()
            except:
                print('not')
            return redirect('ads_admin')
    else:
        return redirect('login_admin')
        

