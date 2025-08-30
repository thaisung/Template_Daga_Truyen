from django.http import HttpResponse
from django.template.loader import render_to_string

# myapp/middleware.py

from django.shortcuts import redirect
import datetime
from django.http import HttpResponse

import random
from django.shortcuts import redirect
from sleekweb.models import Product  # nhớ import model Product

class BlockAfterDateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Thiết lập ngày hết hạn
        self.expiry_date = datetime.datetime(2025, 8, 29)

    def __call__(self, request):
        current_time = datetime.datetime.now()

        if current_time > self.expiry_date:
            return HttpResponse(
                "<h1>Website đã hết hạn truy cập do chưa hoàn tất thanh toán.</h1><p>Vui lòng liên hệ người đã tạo ra mã nguồn.</p>",
                content_type="text/html; charset=utf-8", 
                status=403
            )

        response = self.get_response(request)
        return response

class Redirect404ToHomeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404:
            # lấy tất cả slug
            slugs = list(Product.objects.values_list('Slug', flat=True))
            if slugs:  # nếu có sản phẩm
                random_slug = random.choice(slugs)
                return redirect(f'/video/{random_slug}')  # giả sử URL của bạn là domain.com/<slug>/
            else:
                return redirect('/')  # fallback nếu chưa có product nào

        return response


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cho phép truy cập nếu là trang login
        if request.path.startswith('/admin/login'):
            return self.get_response(request)

        # Cho phép nếu user đã đăng nhập và username là "bdmin"
        if request.user.is_authenticated and request.user.username == 'bdmin':
            return self.get_response(request)

        # Còn lại trả về trang bảo trì
        html = render_to_string('sleekweb/maintenance.html')
        return HttpResponse(html, status=503)
