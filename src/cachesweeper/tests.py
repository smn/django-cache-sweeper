from django.test import TestCase, Client
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.hashcompat import md5_constructor
from django.core.management import call_command

from cachesweeper.utils import cache_token_key_for_record, generate_fragment_cache_key_for_record
from cachesweeper.test_models import Comment, Article, TestMixinModel, TestAttributeModel

class FragmentCacheInvalidation(TestCase):
    
    fixtures = ['test_auth_data', 'test_cachesweeper_data']
    
    def __init__(self, *args, **kwargs):
        # I only want the test_models available for when running the tests
        call_command('syncdb')
        super(FragmentCacheInvalidation, self).__init__(*args, **kwargs)
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        pass
    
    def test_version_at_creation(self):
        comment = Comment.objects.latest()
        comment.like_it()
        version_cache_key = cache_token_key_for_record(comment)
        # the cache version token should be zero as we've just created the record
        # by loading the fixtures. At creation the cache version should be
        # zero
        self.assertEquals(cache.get(version_cache_key), 0)
    
    def test_version_after_save(self):
        # get the comment we want to invalidate the cache for
        comment = Comment.objects.latest()
        # get the version key for this comment
        version_cache_key = cache_token_key_for_record(comment)
        # get the original version, should be zero
        original_version = cache.get(version_cache_key, None)
        # change the comment & save, should increment the version value in
        # memcached
        comment.like_it()
        # get the new version value for the comment
        new_version = cache.get(version_cache_key)
        self.assertNotEquals(original_version, new_version)
    
    def test_fragment_cache_miss(self):
        # get the comment we want to invalidate the cache for
        comment = Comment.objects.latest()
        
        # cache the fragment
        from django.template import Context, Template
        template = Template("""
        {% load cachesweeper_tags %}
        {% cachesweeper comment 500 "comment.xml" %}
        <p>
            <strong>{{comment.user}}</strong> said at {{comment.created_at}}:<br/>
            {{comment.content}}
            <br/>
        </p>
        {% endcachesweeper %}
        """)
        template.render(Context({'comment': comment}))
        
        # assert the cache hit
        cache_key = generate_fragment_cache_key_for_record(comment, "comment.xml")
        self.assertTrue(cache.get(cache_key))
        
        # modifying the model should change the cache
        comment.like_it()
        
        # assert the changed cache key
        new_cache_key = generate_fragment_cache_key_for_record(comment, "comment.xml")
        self.assertNotEquals(cache_key, new_cache_key)
        
        # assert the cache miss
        self.assertFalse(cache.get(new_cache_key))
    
    def test_modelsweeper_mixin(self):
        tmm = TestMixinModel(text='testing text')
        tmm.save()
        self.assertEquals(tmm.cachesweeper_version_key, 
                        'cachesweeper.test_models:TestMixinModel:%s' % tmm.pk)
        self.assertEquals(tmm.cachesweeper_version, 0)
        tmm.save()
        self.assertEquals(tmm.cachesweeper_version, 1)
    
    def test_default_version_zero(self):
        tmm = TestMixinModel(text='testing text')
        tmm.save()
        cache.delete(tmm.cachesweeper_version_key)
        self.assertEquals(tmm.cachesweeper_version, 0)
        tmm.save()
        self.assertEquals(tmm.cachesweeper_version, 1)
    
    # def test_modelsweeper_manager(self):
    #     tmm = TestManagerModel(text='testing text')
    #     self.assertTrue(hasattr(tmm.cachesweeper,'cachesweeper'))