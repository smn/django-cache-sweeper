from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.db.models import F
from myproject.myapp.models import Article, Comment
from myproject.myapp.forms import CommentForm

def articles(request):
    article = Article.objects.latest()
    return HttpResponseRedirect(reverse('article',
                                    kwargs={'article_id': article.pk}))

def article(request, article_id):
    article = Article.objects.get(pk=article_id)
    if request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.save()
            return HttpResponseRedirect(reverse('article', 
                                            kwargs={'article_id':article.pk}))
    else:
        comment_form = CommentForm()
    return render_to_response("article.html", locals(), 
                                context_instance=RequestContext(request))


def dislike(request, article_id, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    comment.like_it()
    comment.save()
    return HttpResponseRedirect(reverse('article',
                                    kwargs={'article_id': article_id}))

def like(request, article_id, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    comment.dislike_it()
    comment.save()
    return HttpResponseRedirect(reverse('article',
                                    kwargs={'article_id': article_id}))