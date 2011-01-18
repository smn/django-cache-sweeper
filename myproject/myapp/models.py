from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.cache import cache
from myapp.utils import invalidate_cache

# Create your models here.
class Article(models.Model):
    """An article"""
    title = models.CharField(blank=True, max_length=100)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        get_latest_by = 'created_at'
    
    def __unicode__(self):
        return self.title
    

class Comment(models.Model):
    """A comment for an article"""
    user = models.ForeignKey(User)
    article = models.ForeignKey(Article)
    content = models.TextField(blank=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        get_latest_by = ordering = ['created_at']
    
    def __unicode__(self):
        return u" - ".join([self.article, self.user, self.content])
    

post_save.connect(invalidate_cache, sender=Comment)