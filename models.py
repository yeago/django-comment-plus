import datetime

from django.db import models

from django.contrib import comments

class Karma(models.Model):
	user = models.ForeignKey('auth.User')
	comment = models.ForeignKey(comments.get_model())
	date_added = models.DateTimeField(default=datetime.datetime.now)
	class Meta:
		unique_together = ('user','comment',)
