from django import template
from django.db.models import Count
from django.contrib.comments.templatetags.comments import BaseCommentNode

register = template.Library()

class KarmaCommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs.annotate(Count('karma')))

def get_karma_comment_list(parser, token):
    return KarmaCommentListNode.handle_token(parser, token)

register.tag(get_karma_comment_list)
