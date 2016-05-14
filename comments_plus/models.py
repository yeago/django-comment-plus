import datetime

from django.db import models
import django_comments

CommentModel = django_comments.get_model()


class Karma(models.Model):
    user = models.ForeignKey('auth.User')
    comment = models.ForeignKey(CommentModel)
    date_added = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        unique_together = ('user', 'comment',)
