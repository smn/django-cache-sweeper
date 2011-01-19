==================================
Django Fragment Cache Invalidation
==================================

Fragment cache invalidation by using a per model version token to prefix the cache keys. The version token can either be an internal memcached counter or a timestamped attribute from the model, such as `updated_at`.

Installation
------------

Install with `pip` or with `python setup.py install` and add 'cachesweeper' to your `settings.INSTALLED_APPS`


post_save cache sweeper
-----------------------

An example setup; an article has many comments, each comment is cached, a single vote should invalidate the comment's specific cached fragment as well as the total article's page.
    
**Template fragment caching**

`{% cachesweeper %}` takes a Django ORM model as its first argument, the expiry time as its second and any following arguments are used to construct the rest of the cache key

::

    {% load markup %}
    {% load cachesweeper_tags %}
    {% cachesweeper comment 500 "comment.xml" %}
    <p>
        <strong>{{comment.user}}</strong> said at {{comment.created_at}}:<br/>
        {{comment.content|markdown}}
        <br/>
        <a href={% url like article_id=article.pk,comment_id=comment.pk %}>Like ({{comment.likes.count}})</a>
        <a href={% url dislike article_id=article.pk,comment_id=comment.pk %}>Dislike ({{comment.dislikes.count}})</a>
    </p>
    {% endcachesweeper %}

**Invalidating the fragment when the model changes**

On a post_save invalidate the cache for the given model. There are two options, either have Memcached keep an internal version counter for each model or using the keyword `using` as a means of versioning the cache.

::
    
    from cachesweeper.utils import invalidate_cache_for
    
    # using Memcached's internal counter
    def invalidate_vote_cache(sender, **kwargs):
        vote = kwargs.get('instance')
        invalidate_cache_for(vote.comment)
    
    post_save.connect(invalidate_vote_cache, sender=Vote)
    
    
    # using a model's attribute
    def invalidate_article_cache(sender, **kwargs):
        article = kwargs.get('instance')
        invalidate_cache_for(article, using='updated_at')
    
    post_save.connect(invalidate_article_cache, sender=Article)

