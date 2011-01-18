from django.test import TestCase, Client
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.hashcompat import md5_constructor
from myproject.myapp.models import Comment, Article
from myproject.myapp.utils import cache_token_key_for_record

def generate_fragment_key(record, *cache_keys):
    unique_fragment_key = u":".join(map(lambda key: urlquote(str(key)), cache_keys))
    unique_fragment_key_hash = md5_constructor(unique_fragment_key)
    model_version_key = cache_token_key_for_record(record)
    model_current_version = cache.get(model_version_key, 0)
    cache_key = 'template.%s.%s.%s' % (
            model_version_key, 
            model_current_version,
            unique_fragment_key_hash.hexdigest()
    )
    return cache_key
    

class FragmentCacheInvalidation(TestCase):
    
    fixtures = ['test_auth_data', 'test_myapp_data']
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_version_at_creation(self):
        comment = Comment.objects.latest()
        version_cache_key = cache_token_key_for_record(comment)
        # the cache version token should be zero as we've just created the record
        # by loading the fixtures. At creation the cache version should be
        # zero
        self.assertTrue(cache.get(version_cache_key))
    
    def test_version_after_save(self):
        # get the comment we want to invalidate the cache for
        comment = Comment.objects.latest()
        # get the version key for this comment
        version_cache_key = cache_token_key_for_record(comment)
        # get the original version, should be zero
        original_version = cache.get(version_cache_key)
        self.assertTrue(original_version)
        # change the comment & save, should increment the version value in
        # memcached
        comment.like_it()
        comment.save()
        # get the new version value for the comment
        new_version = cache.get(version_cache_key)
        self.assertNotEquals(original_version, new_version)
    
    def test_fragment_cache_miss(self):
        # get the comment we want to invalidate the cache for
        comment = Comment.objects.latest()
        # populate the fragment cache
        client = Client()
        response = client.get(reverse('articles'), follow=True)
        
        # assert the cache hit
        cache_key = generate_fragment_key(comment, "comment.xml")
        self.assertTrue(cache.get(cache_key))
        
        # modifying the model should change the cache
        comment.like_it()
        comment.save()
        
        # assert the changed cache key
        new_cache_key = generate_fragment_key(comment, "comments.xml")
        self.assertNotEquals(cache_key, new_cache_key)
        
        # assert the cache miss
        self.assertFalse(cache.get(new_cache_key))