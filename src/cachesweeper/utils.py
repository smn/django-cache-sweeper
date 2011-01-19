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

def invalidate_cache_handler(sender, **kwargs):
    """
    signal handler for invalidating the cache for a single record
    """
    instance = kwargs.get('instance')
    return invalidate_cache_for(instance)


def invalidate_cache_for(record,using=None):
    """
    invalidate the cache for the given ORM record
    """
    return update_cache_token_for_record(record, using)

def update_cache_token_for_record(instance, using):
    """
    update the cached versioning token for the given record. All 
    {% cachesweeper %} fragment caches use the cached version token to
    store the cached data. If the token is changed all fragment caches
    will eventually expire.
    """
    if using:
        return update_cache_token_for_record_with_attribute(instance, using)
    else:
        return update_cache_token_for_record_with_counter(instance)

def update_cache_token_for_record_with_attribute(instance, token_attr):
    """
    Update the token with a value read from an attribute of the ORM's record 
    """
    cache_key = cache_token_key_for_record(instance)
    token_value = getattr(instance,token_attr)
    token_value_hash = md5_constructor(str(token_value)).hexdigest()
    cache.set(cache_key, token_value_hash, 0) # 0 = no time based expiry

def update_cache_token_for_record_with_counter(instance):
    """
    Update the cache token with an internal memcached counter. 
    """
    cache_key = cache_token_key_for_record(instance)
    value = cache.get(cache_key)
    if value == None or not isinstance(value, int):
        cache.set(cache_key, 0, 0) # 0 = no time based expiry
    else:
        cache.incr(cache_key)
    


def generate_fragment_cache_key_for_record(record, *cache_keys):
    unique_fragment_key = u":".join(map(lambda key: urlquote(str(key)), cache_keys))
    unique_fragment_key_hash = md5_constructor(unique_fragment_key)
    record_version_key = cache_token_key_for_record(record)
    record_current_version = cache.get(record_version_key)
    cache_key = 'cachesweeper.%s.%s.%s' % (
            record_version_key, 
            record_current_version,
            unique_fragment_key_hash.hexdigest()
    )
    return cache_key