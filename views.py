from django.http import HttpResponse
from django.contrib import comments
from django.shortcuts import get_object_or_404
from comments_plus import models as cmodels

CommentModel = comments.get_model()

def karma_add(request,id):
	comment = get_object_or_404(CommentModel,pk=id)
	if comment.user and request.user == comment.user:
		return HttpResponse("")

	cmodels.Karma.objects.get_or_create(user=request.user,comment=comment)
	return HttpResponse("")

def karma_remove(request,id):
	return HttpRespons("")
