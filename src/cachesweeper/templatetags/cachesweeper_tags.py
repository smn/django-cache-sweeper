from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor
from django.db.models import Model
from django.conf import settings
from cachesweeper.utils import cache_token_key_for_record, generate_fragment_cache_key_for_record

register = Library()

class CacheSweeperNode(Node):
    def __init__(self, nodelist, model, expire_time, cache_keys):
        self.nodelist = nodelist
        self.model_var = Variable(model)
        self.expire_time_var = Variable(expire_time)
        self.cache_key_vars = [Variable(key) for key in cache_keys]
    
    def get_expire_time(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cachesweeper" tag got an unknown variable: %r' % self.expire_time_var.var)
        
        try:
            return int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"cachesweeper" tag got a non-integer timeout value: %r' % expire_time)
        
    
    def get_model(self, context):
        try:
            model = self.model_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cachesweeper" tag got an unknown variable: %r' % self.model_var.var)
        if not isinstance(model,Model):
            raise TemplateSyntaxError('"cachesweeper" tag model should be an instance of django.db.models.Model, got: %s' % model)
        return model
    
    def render(self, context):
        expire_time = self.get_expire_time(context)
        model = self.get_model(context)
        unique_fragment_cache_keys = [var.resolve(context) 
                                        for var in self.cache_key_vars]
        cache_key = generate_fragment_cache_key_for_record(model, *unique_fragment_cache_keys)
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache.set(cache_key, value, expire_time)
        return value
        
    


@register.tag
def cachesweeper(parser, token):
    nodelist = parser.parse(('endcachesweeper',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) < 4:
        raise TemplateSyntaxError(u"'%s' tag requires at least 3 arguments" % tokens[0])
    model, expire_time, cache_keys = tokens[1], tokens[2], tokens[3:]
    return CacheSweeperNode(nodelist, model, expire_time, cache_keys)