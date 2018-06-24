from django import template
from django.template.loader import render_to_string
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django_comments.templatetags.comments import BaseCommentNode
import django_comments

Comment = django_comments.get_model()

register = template.Library()


class RemoveCommentNode(template.Node):
    def __init__(self, user, object, var_name):
        self.user = template.Variable(user)
        self.object = template.Variable(object)
        self.var_name = var_name

    def render(self, context):
        object = self.object.resolve(context)
        user = self.user.resolve(context)
        var = self.var_name
        if hasattr(object, 'comment_remove_by'):
            if object.comment_remove_by(user):
                context[var] = True
        return ''


def set_comment_remove_variable(parser, token):
    args = token.split_contents()
    if not len(args) in [4, 6]:
        raise template.TemplateSyntaxError("Not the right amount of args")

    return RemoveCommentNode(args[2], args[3], args[5])

register.tag(set_comment_remove_variable)


@register.simple_tag(takes_context=True)
def render_comment_stage(context, instance, since=None, until=None, template=None, comments=None, hide_form=False):
    ctype = ContentType.objects.get_for_model(instance)
    templates = [template] if template else [
        "comments/%s/%s/stage.html" % (ctype.app_label, ctype.model),
        "comments/%s/stage.html" % ctype.app_label,
        "comments/stage.html"
    ]
    if comments is None:
        comments = Comment.objects.for_model(instance)
    if since:
        comments = comments.filter(submit_date__gt=since)
    if until:
        comments = comments.filter(submit_date__lt=until)

    request = context.get('request')

    render_context = {
        "request": request,
        "object": instance,
        'comment_list': comments,
        'hide_form': hide_form,
    }

    stagestr = render_to_string(
        templates,
        render_context,
        request=request)
    context.pop()
    return stagestr
