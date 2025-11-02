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



    
def channel_admin(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        context['list_Channel'] = Channel.objects.all().order_by('Count')
        s = request.GET.get('s')
        if s:
            context['list_Channel'] = context['list_Channel'].filter(Q(Title__icontains=s)).order_by('-id')
            context['s'] = s
        # print('context:',context)
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'sleekweb/admin/channel_admin.html', context, status=200)
        else:
            return redirect('login_admin')
        

def channel_add_admin(request):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Name'] = request.POST.get('Name')
            fields['Key'] = request.POST.get('Key')
            fields['Avatar'] = request.FILES.get('Avatar')
            obj = Channel.objects.create(**fields)
            return redirect('channel_admin')
        else:
            return redirect('login_admin')
    
def channel_edit_admin(request,pk):
    if request.method == 'GET':
        return redirect('login_admin')
    elif request.method == 'POST':
        if request.user.is_authenticated and request.user.is_superuser:
            fields = {}
            fields['Name'] = request.POST.get('Name')
            fields['Key'] = request.POST.get('Key')
            fields['Count'] = request.POST.get('Count')
            fields['Avatar'] = request.FILES.get('Avatar')

            obj = Channel.objects.get(pk=pk)

            if fields['Name']:
                obj.Name = fields['Name']
            if fields['Key']:
                obj.Key = fields['Key']
            if fields['Count']:
                obj.Count = fields['Count']
            if fields['Avatar']:
                obj.Avatar.delete(save=False)
                obj.Avatar = fields['Avatar']

            obj.save()
            return redirect('channel_admin')
        else:
            return redirect('login_admin')
    
def channel_remove_admin(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST':
            try:
                obj = Channel.objects.get(pk=pk)
                if obj.Avatar:
                    obj.Avatar.delete(save=False)
                obj.delete()
            except:
                print('not')
            return redirect('channel_admin')
    else:
        return redirect('login_admin')
        

