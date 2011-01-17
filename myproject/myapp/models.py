from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.cache import cache

# Create your models here.
class Article(models.Model):
    """An article"""
    title = models.CharField(blank=True, max_length=100)
    text = models.TextField(blank=True)

    def __unicode__(self):
        return self.title
    

class Comment(models.Model):
    """A comment for an article"""
    user = models.ForeignKey(User)
    article = models.ForeignKey(Article)
    content = models.TextField(blank=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    
    def __unicode__(self):
        return u" - ".join([self.article, self.user, self.content])
    

def cache_key(record):
    klass = record.__class__
    return ":".join([klass.__name__, klass.__module__, record.pk])

def increment_cached_version(sender, **kwargs):
    created = kwargs.get('created', False)
    instance = kwargs.get('instance')
    cache_key = cache_key(instance)
    if not cache.get(cache_key)
        cache.set(cache_key, 0)
    else:
        cache.incr(cache_key)

post_save.connect(increment_cached_version, sender=Comment)