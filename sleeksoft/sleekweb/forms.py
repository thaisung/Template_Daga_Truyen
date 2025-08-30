from django import forms
from .models import *
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['Title', 'Content','Avatar']

class ttgt1Form(forms.ModelForm):
    class Meta:
        model = Edit_ttgt1
        fields = ['Title','Category', 'Content','Photo']

class Edit_kqls1_Form(forms.ModelForm):
    class Meta:
        model = Edit_kqls1
        fields = ['Content']

