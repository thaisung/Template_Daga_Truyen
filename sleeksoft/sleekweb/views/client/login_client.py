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



def login_view(request):
    if request.method == 'GET':
        context = {}
        context['domain'] = settings.DOMAIN
        print('context:',context)
        if request.user.is_authenticated:
            return redirect('product')
        else:
            return render(request, 'sleekweb/client/login.html', context, status=200)
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username is None or password is None:
            return JsonResponse({'success': False, 'message': 'Hành động đăng nhập của bạn không được chấp nhận.Hãy lên trang chính thức của WEBSITE để đăng nhập.'})
        elif not username or not password:
            return JsonResponse({'success': False, 'message': 'Điền đầy đủ thông tin trước khi đăng nhập.'})
        else:
            if User.objects.filter(username=username).exists():
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return JsonResponse({'success': True, 'redirect_url': reverse('product')})
                    else:
                        return JsonResponse({'success': False, 'message': 'Tài khoản của bạn đã ngừng hoạt động'})
                else:
                    return JsonResponse({'success': False, 'message': 'Mật khẩu đăng nhập không chính xác'})
            else:
                return JsonResponse({'success': False, 'message': 'Tên tài khoản đăng nhập không chính xác'})
    
def logout(request):
    logout(request)
    return redirect('login')

    
