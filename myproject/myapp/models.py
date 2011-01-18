from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.cache import cache
from myapp.utils import invalidate_cache_handler

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
    
    # cache_version_token = 'updated_at'
    
    def like_it(self):
        self.likes += 1
    
    def dislike_it(self):
        self.dislikes += 1
    
    class Meta:
        get_latest_by = 'created_at'
        ordering = ['created_at']
    
    def __unicode__(self):
        return u" - ".join(map(str, [self.article, self.user, self.content]))
    

post_save.connect(invalidate_cache_handler, sender=Comment)