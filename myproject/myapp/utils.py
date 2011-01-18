from django.core.cache import cache
from django.utils.http import urlquote
from django.utils.hashcompat import md5_constructor

def cache_token_key_for_record(record):
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
    instance = kwargs.get('instance')
    return update_cache_token_for_record(instance)

def update_cache_token_for_record(instance):
    cache_key = cache_token_key_for_record(instance)
    token_attr = getattr(instance, 'cache_version_token','updated_at')
    token_value = getattr(instance,token_attr)
    token_value_hash = md5_constructor(str(token_value)).hexdigest()
    cache.set(cache_key, token_value_hash)


def generate_fragment_cache_key_for_record(record, *cache_keys):
    unique_fragment_key = u":".join(map(lambda key: urlquote(str(key)), cache_keys))
    unique_fragment_key_hash = md5_constructor(unique_fragment_key)
    record_version_key = cache_token_key_for_record(record)
    record_current_version = cache.get(record_version_key)
    cache_key = 'template.%s.%s.%s' % (
            record_version_key, 
            record_current_version,
            unique_fragment_key_hash.hexdigest()
    )
    return cache_key