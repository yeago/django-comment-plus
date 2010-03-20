from django.conf.urls.defaults import *


urlpatterns = patterns('comments_plus.views',
	url('(?P<id>\d+)/karma-add/$','karma_add',name="karma_add"),
	url('(?P<id>\d+)/karma-remove/$','karma_remove',name="karma_remove"),
)
