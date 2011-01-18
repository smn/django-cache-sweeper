from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from django.core.cache import cache
from django.utils.http import urlquote
from django.utils.hashcompat import md5_constructor
from django.db.models import Model
from django.conf import settings
from myproject.myapp.utils import cache_token_key_for_record

register = Library()

class ModelCacheNode(Node):
    def __init__(self, nodelist, model, expire_time, cache_keys):
        self.nodelist = nodelist
        self.model_var = Variable(model)
        self.expire_time_var = Variable(expire_time)
        self.cache_key_vars = [Variable(key) for key in cache_keys]
    
    def get_expire_time(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"modelcache" tag got an unknown variable: %r' % self.expire_time_var.var)
        
        try:
            return int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"modelcache" tag got a non-integer timeout value: %r' % expire_time)
        
    
    def get_model(self, context):
        try:
            model = self.model_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"modelcache" tag got an unknown variable: %r' % self.model_var.var)
        if not isinstance(model,Model):
            raise TemplateSyntaxError('"modelcache" tag model should be an instance of django.db.models.Model, got: %s' % model)
        return model
    
    def render(self, context):
        expire_time = self.get_expire_time(context)
        model = self.get_model(context)
        unique_fragment_key = u':'.join([
                                        urlquote(var.resolve(context)) 
                                        for var in self.cache_key_vars
                                    ])
        unique_fragment_key_hash = md5_constructor(unique_fragment_key)
        model_version_key = cache_token_key_for_record(model)
        # default to zero for versioning if it doesn't exist
        model_current_version = cache.get(model_version_key, 0)
        cache_key = 'template.%s.%s.%s' % (
                model_version_key, 
                model_current_version,
                unique_fragment_key_hash.hexdigest()
        )
        value = cache.get(cache_key)
        if value is None:
            value = self.nodelist.render(context)
            cache.set(cache_key, value, expire_time)
        return value
        
    


@register.tag
def modelcache(parser, token):
    nodelist = parser.parse(('endmodelcache',))
    parser.delete_first_token()
    tokens = token.split_contents()
    if len(tokens) < 4:
        raise TemplateSyntaxError(u"'%s' tag requires at least 3 arguments" % tokens[0])
    model, expire_time, cache_keys = tokens[1], tokens[2], tokens[3:]
    return ModelCacheNode(nodelist, model, expire_time, cache_keys)