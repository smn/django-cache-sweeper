from django.core.cache import cache

def cache_key_for_record(record):
    """
    Create a unique cache key prefix for a given Django ORM record
    
    >>> from django.contrib.auth.models import User
    >>> cache_key_for_record(User(pk=1))
    'django.contrib.auth.models:User:1'
    >>> 
    
    """
    klass = record.__class__
    return ":".join(map(str, [klass.__module__, klass.__name__, record.pk]))

def invalidate_cache(sender, **kwargs):
    created = kwargs.get('created', False)
    instance = kwargs.get('instance')
    return increment_cache_id_for_record(instance)

def increment_cache_id_for_record(instance):
    cache_key = cache_key_for_record(instance)
    if not cache.get(cache_key):
        cache.set(cache_key, 0)
    else:
        cache.incr(cache_key)

