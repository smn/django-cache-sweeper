from django.conf.urls.defaults import *
from myproject.myapp import views

urlpatterns = patterns('',
    (r'^$', views.articles, {}, 'articles'),
    (r'^article/(?P<article_id>\d+)/$', views.article, {}, 'article'),
    (r'^article/(?P<article_id>\d+)/like/(?P<comment_id>\d+)/$', views.like, {}, 'like'),
    (r'^article/(?P<article_id>\d+)/dislike/(?P<comment_id>\d+)/$', views.dislike, {}, 'dislike'),
)
