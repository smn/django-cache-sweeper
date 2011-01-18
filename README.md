Django Fragment Cache Invalidation
==================================

Fragment cache invalidation by using a per model version token to prefix the cache keys. The version token can either be an internal memcached counter or a timestamped attribute from the model, such as `updated_at`.

post_save cache sweeper
-----------------------

An example setup; an article has many comments, each comment is cached, a single vote should invalidate the comment's specific cached fragment as well as the total article's page.
    
    def invalidate_vote_cache(sender, **kwargs):
        vote = kwargs.get('instance')
        invalidate_cache_for(vote.comment)
    
    post_save.connect(invalidate_vote_cache, sender=Vote)
