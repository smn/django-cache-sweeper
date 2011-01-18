from django.contrib import admin
from myproject.myapp.models import Article, Comment

admin.site.register(Article)
admin.site.register(Comment)