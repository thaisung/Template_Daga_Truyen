from django.db import models

# Create your models here.
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin

from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify

# Create your models here.

class User(AbstractUser):
    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Quản lý tài khoản Đăng Nhập"
    AbstractUser._meta.get_field('email').blank = False
    AbstractUser._meta.get_field('email').blank = False
    AbstractUser._meta.get_field('username').blank = False
    AbstractUser._meta.get_field('username').blank = False
    AbstractUser._meta.get_field('password').blank = False
    AbstractUser._meta.get_field('password').blank = False
    
    Avatar = models.ImageField(upload_to='user_image', default="user_image/user_empty.png", null=True,blank=True)
    Full_name = models.CharField('Họ và tên', max_length=255,blank=True, null=True)
    Phone_number = models.CharField('Số điện thoại', max_length=255,blank=True, null=True)
    OTP = models.CharField('Mã Otp',max_length=255, null=True,blank=True)
    Creation_time = models.DateTimeField('Thời gian tạo',auto_now_add=True)
    Update_time = models.DateTimeField('Thời gian cập nhật',auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['Full_name']),
        ]

class Product(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Sản phẩm"
    
    Title = models.CharField('Tiêu đề', max_length=200,blank=True, null=True)
    Slug = models.SlugField(unique=True, blank=True, null=True)
    Description = models.TextField('Mô tả',blank=True, null=True)
    Avatar = models.ImageField(upload_to='Avatar_Product', null=True,blank=True)
    Video = models.FileField(upload_to='Video_Product', null=True, blank=True)
    Link = models.CharField('Link video', max_length=10000,blank=True, null=True)
    Iframe = models.CharField('Iframe video', max_length=10000,blank=True, null=True)
    Creation_time = models.DateTimeField('Thời gian tạo',auto_now_add=True)
    Update_time = models.DateTimeField('Thời gian cập nhật',auto_now=True)

    def save(self, *args, **kwargs):
        # Tạo slug từ Title nếu chưa có
        if self.Title and not self.Slug:
            base_slug = slugify(self.Title)
            slug = base_slug
            counter = 1
            # Đảm bảo slug là unique
            while Product.objects.filter(Slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.Slug = slug
        super().save(*args, **kwargs)

class Ads(models.Model):
    class Meta:
        ordering = ["id"]
        verbose_name_plural = "Quảng cáo"
    
    Script = models.CharField('Script', max_length=1000,blank=True, null=True)
    Count = models.IntegerField('Số',blank=True, null=True)
    Creation_time = models.DateTimeField('Thời gian tạo',auto_now_add=True)
    Update_time = models.DateTimeField('Thời gian cập nhật',auto_now=True)
