from django.forms import ModelForm
from myproject.myapp.models import Comment

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('user','content',)